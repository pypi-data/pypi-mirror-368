import redis
import random
import string
import threading
import json
import time
from typing import Any, Callable, Optional
from simple_parsing import parse
from dataclasses import dataclass, field
from contextlib import contextmanager
from pathlib import Path
from functools import wraps
from queue import Queue

JSON_PATH = str(Path(__file__).parent / "distributions.json")

def cg_method(cmd_type, can_create_key):
    """Decorator for command-generator methods that sets required attributes."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        setattr(wrapper, 'type', cmd_type)
        setattr(wrapper, 'can_create_key', can_create_key)
        return wrapper
    return decorator

@contextmanager
def exception_wrapper():
    """
    Suppresses ResponseError exceptions that are expected to occur during the execution of 
    randomally generated Redis commands. All other exceptions are raised.
    """
    try:
        yield
    except redis.exceptions.ResponseError as e:
        if (("WRONGTYPE" not in str(e)) and
            ("MOVED" not in str(e)) and
            ("item exists" not in str(e)) and
            ("key already exists" not in str(e)) and
            ("Keys in request don't hash to the same slot" not in str(e)) and
            (not ("TS." in str(e) and "the key does not exist" in str(e))) and
            (not ("BF." in str(e) and "received bad data" in str(e))) and
            (not ("CF." in str(e) and "Invalid header" in str(e))) and
            (not ("CMS." in str(e) and "width/depth is not equal" in str(e))) and
            (not ("INCRBY" in str(e) and "value is not an integer or out of range" in str(e))) and
            (not ("JSON." in str(e) and "could not perform this operation on a key that doesn't exist" in str(e))) and 
            (not ("JSON." in str(e) and "Path" in str(e) and "does not exist" in str(e))) and
            (not ("XGROUP CREATE" in str(e) and "BUSYGROUP Consumer Group name already exists" in str(e))) and
            (not ("GEO" in str(e) and "could not decode requested zset member" in str(e))) and
            (not ("RENAME" in str(e) and "no such key" in str(e))) and
            (not ("RESTORE" in str(e))) and
            (not ("LSET" in str(e) and "index out of range" in str(e))) and
            (not ("LSET" in str(e) and "no such key" in str(e)))):
            raise e

class KeyedLimitedRandomQueue:
    def __init__(self, max_size_per_key=100):
        self.max_size_per_key = max_size_per_key
        self.queues = {}
        self.lock = threading.RLock()
    
    def put(self, key, item):
        with self.lock:
            if key not in self.queues:
                self.queues[key] = Queue(maxsize=self.max_size_per_key)
            
            queue = self.queues[key]
            if queue.full():
                queue.get()  # Remove oldest item
            queue.put(item)
    
    def get(self, key):
        with self.lock:
            if key in self.queues:
                try:
                    return random.choice(self.queues[key].queue)
                except:
                    pass
            return None

class RedisObj():
    """
    A wrapper class for the redis.Redis client that intercepts method calls
    and wraps them in an exception handling context manager.
    """

    def __init__(self, *args, **kwargs):
        self._client = redis.Redis(*args, **kwargs)

    def __getattr__(self, name):
        """
        Retrieves the attribute from the underlying Redis client. If the attribute
        is callable, it wraps the method call in the exception_wrapper context manager.
        """
        original_attr = getattr(self._client, name)

        if callable(original_attr):
            def wrapper(*args, **kwargs):
                with exception_wrapper():
                    return original_attr(*args, **kwargs)
            return wrapper
        else:
            return original_attr

@dataclass
class BaseGen():
    verbose: bool = False  # Print debug information (sent commands)
    hosts: tuple = ("localhost:6379",)  # Redis hosts to connect to
    flush: bool = False  # Flush all hosts on connection
    max_cmd_cnt: int = 10000  # Maximum number of commands to execute, may be interrupted by exceeding memory cap. Set to 0 for infinite
    mem_cap: float = 70  # Memory cap percentage
    pipe_every_x: int = 1000  # Execute pipeline every X commands
    def_key_size: int = 10  # Default key size
    def_key_pref: str = '' # Default key prefix
    distributions: str = None # distributions.json file path or a serialized dict (e.g. {"expire": 50, "incrby": 70, ...})
    expire_precentage: int = 0  # Percentage of commands with expiry/ttl
    logfile: str = None  # Optional log file path to write debug information to
    maxmemory_bytes: int = None  # Override INFO's maxmemory (useful when unavailable, for e.g. in cluster mode)
    print_prefix: str = "COMMAND GENERATOR: "
    identical_values_across_hosts: bool = False  # Generate identical commands across connections, or allow value conflicts
    max_generated_values_per_type: int = 100  # Maximum number of values to generate for each type
    keyed_limited_random_queue: Optional[KeyedLimitedRandomQueue] = None
    
    ttl_low: int = 15
    ttl_high: int = 300

    ########################################
    ######## Internal use methods ##########
    ########################################
    
    UNSCANNABLE_TYPES = ["hll", "bit", "geo"]

    def _rand_str(self, str_size: int) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k = str_size))
    
    def _rand_key(self, type: str, hash_tag = None) -> str:
        prefix = self.def_key_pref + f"{hash_tag}:" if hash_tag else ""

        # The following types can't be directly scanned, so we must add a prefix to distinguish them
        prefix += f"{type}:" if type in self.UNSCANNABLE_TYPES else ""
        
        return prefix + self._rand_str(self.def_key_size)
    
    def _scan_rand_key(self, redis_obj: redis.Redis, type: str) -> str | None:
        if type == "base":
            return redis_obj.randomkey()
        
        if not hasattr(self, 'scan_cursors'):
            self.scan_cursors = {}
        
        conn = self._get_conn_info(redis_obj)
        if conn not in self.scan_cursors:
            self.scan_cursors[conn] = {}
        
        if type not in self.scan_cursors[conn]:
            self.scan_cursors[conn][type] = 0

        if type not in self.UNSCANNABLE_TYPES:
            cursor, keys = redis_obj.scan(self.scan_cursors[conn][type], _type=type)
        else:
            scan_match = f"{self.def_key_pref}{type}:*"
            cursor, keys = redis_obj.scan(self.scan_cursors[conn][type], match=scan_match)
        self.scan_cursors[conn][type] = cursor
        return random.choice(keys) if keys else None

    def _put_rand_value(self, key: str, value: Any) -> None:
        assert self.keyed_limited_random_queue is not None
        self.keyed_limited_random_queue.put(key, value)

    def _get_rand_value(self, key: str) -> Optional[Any]:        
        assert self.keyed_limited_random_queue is not None
        return self.keyed_limited_random_queue.get(key)
    
    def _check_mem_cap(self, redis_obj: redis.Redis):
        info = redis_obj.info()
        
        if self.maxmemory_bytes:
            max_mem = self.maxmemory_bytes
        else:
            max_mem = info['maxmemory'] if ('maxmemory' in info) else None
        
        curr_mem = info['used_memory']
        
        if max_mem and curr_mem >= (self.mem_cap / 100) * max_mem:
            self._print(f"Memory cap for {self._get_conn_info(redis_obj)} reached, with {curr_mem} bytes used out of {max_mem * (self.mem_cap / 100)} available")
            return True
        else:
            return False
    
    def _get_conn_info(self, redis_obj: redis.Redis) -> str:
        return f"{redis_obj.connection_pool.connection_kwargs['host']}:{redis_obj.connection_pool.connection_kwargs['port']}"
    
    def _pipe_to_redis(self, pipe: redis.client.Pipeline) -> RedisObj:
        return RedisObj(connection_pool=pipe.connection_pool)
    
    def _print(self, msg: str) -> None:
        if self.file:
            self.file.write(f"{msg}\n")
        
        if self.verbose:
            print(self.print_prefix + msg)
    
    def _extract_distributions(self) -> None:
        if self.distributions is None:
            self.distributions = JSON_PATH
        
        if self.distributions.endswith('.json'):
            with open(self.distributions, 'r') as f:
                self.distributions = json.load(f)
        else:
            self.distributions = json.loads(self.distributions)
        
        method_names = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith('_')]
        for cmd in self.distributions:
            if cmd not in method_names:
                raise ValueError(f"Command '{cmd}' not found in generator")
    
    def _run(self, stop_event: threading.Event = None, keyed_limited_random_queue: KeyedLimitedRandomQueue = KeyedLimitedRandomQueue(100)) -> None:
        self.keyed_limited_random_queue = keyed_limited_random_queue
        self.file = open(self.logfile, 'w') if self.logfile else None
        rl = []  # Redis connections list
        redis_pipes = []
        
        try:
            self._extract_distributions()
            
            for host in self.hosts:
                (hostname, port) = host.split(':')
                r = redis.Redis(host=hostname, port=port)
                r.ping()
                
                if self.flush:
                    r.flushall()
                self._print("INFO: " + str(r.info()))
                
                rl.append(r)
                redis_pipes.append(r.pipeline(transaction=False))
            
            i = 1
            while self.max_cmd_cnt == 0 or i <= self.max_cmd_cnt:
                if stop_event and stop_event.is_set():
                    break
                for r in rl:
                    if self._check_mem_cap(r):
                        return
                
                key = None
                should_expire = False  # Whether generated key should have a TTL
                cmd_name = random.choices(list(self.distributions.keys()), weights=list(self.distributions.values()))[0]
                cmd = getattr(self, cmd_name)
                
                # Generate a single key for all hosts. In case the command can add keys, we'd prefer to generate
                # a new keyname to increase DBSIZE. Otherwise, we'd prefer to act upon an existing key
                if cmd.can_create_key:
                    key = self._rand_key(cmd.type)
                    
                    if random.randint(0, 99) < self.expire_precentage:
                        should_expire = True
                else:
                    r = random.choice(rl)  # Randomly select a connection for scanning
                    key = self._scan_rand_key(r, cmd.type)
                        
                    if not key:
                        continue  # Skip if no key found, e.g. in case of empty DB or no keys of the requested type

                # Generate command with common seed accross hosts if `identical_values_across_hosts`
                if self.identical_values_across_hosts:
                    seed = time.time()
                
                for pipe in redis_pipes:
                    if self.identical_values_across_hosts:
                        random.seed(seed)
                    cmd(pipe, key)
                    
                    if should_expire:
                        self.expire(pipe, key)

                if i % self.pipe_every_x == 0:
                    for (pipe, r) in zip(redis_pipes, rl):
                        self._print(f"Executing pipeline for {self._get_conn_info(r)}")
                        for command in pipe.command_stack:
                            self._print(f"Command: {command[0]}")
                        
                        with exception_wrapper():
                            pipe.execute()
                
                i += 1
            
            # Execute remaining commands
            for pipe in redis_pipes:
                with exception_wrapper():
                    pipe.execute()
        
        except Exception as e:
            self._print(f"Exception: {e}")
            raise e
        
        finally:
            for r in rl:
                self._print("Connection: " + self._get_conn_info(r))
                self._print("Memory usage: " + str(r.info()['used_memory']))
                self._print("DB size: " + str(r.dbsize()))
                r.close()
            self.file.close() if self.file else None
    
    ########################################
    ######## Redis command methods #########
    ########################################
    
    @cg_method("base", False)
    def expire(self, pipe: redis.client.Pipeline, key: str) -> None:
        seconds = random.randrange(self.ttl_low, self.ttl_high)
        
        # Optional expiration conditions (Redis 7.0+)
        kwargs = {}
        if random.random() < 0.3:
            kwargs['nx'] = True  # Set expiry only if key has no expiry
        elif random.random() < 0.3:
            kwargs['xx'] = True  # Set expiry only if key already has expiry
        elif random.random() < 0.2:
            kwargs['gt'] = True  # Set expiry only if new expiry is greater than current
        elif random.random() < 0.2:
            kwargs['lt'] = True  # Set expiry only if new expiry is less than current
        
        pipe.expire(key, seconds, **kwargs)
    
    @cg_method("base", False)
    def pexpire(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Expire in milliseconds (more precise)
        milliseconds = random.randrange(self.ttl_low * 1000, self.ttl_high * 1000)
        
        # Optional expiration conditions
        kwargs = {}
        if random.random() < 0.3:
            kwargs['nx'] = True
        elif random.random() < 0.3:
            kwargs['xx'] = True
        elif random.random() < 0.2:
            kwargs['gt'] = True
        elif random.random() < 0.2:
            kwargs['lt'] = True
            
        pipe.pexpire(key, milliseconds, **kwargs)
    
    @cg_method("base", False)
    def expireat(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Expire at absolute Unix timestamp (seconds)
        import time
        future_timestamp = int(time.time()) + random.randrange(self.ttl_low, self.ttl_high)
        
        # Optional expiration conditions
        kwargs = {}
        if random.random() < 0.3:
            kwargs['nx'] = True
        elif random.random() < 0.3:
            kwargs['xx'] = True
        elif random.random() < 0.2:
            kwargs['gt'] = True
        elif random.random() < 0.2:
            kwargs['lt'] = True
            
        pipe.expireat(key, future_timestamp, **kwargs)
    
    @cg_method("base", False)
    def pexpireat(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Expire at absolute Unix timestamp (milliseconds)
        import time
        future_timestamp_ms = int(time.time() * 1000) + random.randrange(self.ttl_low * 1000, self.ttl_high * 1000)
        
        # Optional expiration conditions
        kwargs = {}
        if random.random() < 0.3:
            kwargs['nx'] = True
        elif random.random() < 0.3:
            kwargs['xx'] = True
        elif random.random() < 0.2:
            kwargs['gt'] = True
        elif random.random() < 0.2:
            kwargs['lt'] = True
            
        pipe.pexpireat(key, future_timestamp_ms, **kwargs)
    
    @cg_method("base", False)
    def persist(self, pipe: redis.client.Pipeline, key: str) -> None:
        pipe.persist(key)
    
    @cg_method("base", False)
    def ttl(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Get time-to-live in seconds
        pipe.ttl(key)
    
    @cg_method("base", False)
    def pttl(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Get time-to-live in milliseconds
        pipe.pttl(key)
    
    @cg_method("base", False)
    def expiretime(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Get absolute expiration timestamp in seconds (Redis 7.0+)
        pipe.expiretime(key)
    
    @cg_method("base", False)
    def pexpiretime(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Get absolute expiration timestamp in milliseconds (Redis 7.0+)
        pipe.pexpiretime(key)

    # Key management family - comprehensive key lifecycle operations
    @cg_method("base", False)
    def delete(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Delete one or more keys
        redis_obj = self._pipe_to_redis(pipe)
        
        # Sometimes delete multiple keys at once
        if random.random() < 0.3:
            additional_keys = []
            for _ in range(random.randint(1, 3)):
                extra_key = redis_obj.randomkey()
                if extra_key:
                    additional_keys.append(extra_key)
            
            if additional_keys:
                pipe.delete(key, *additional_keys)
            else:
                pipe.delete(key)
        else:
            pipe.delete(key)
    
    @cg_method("base", False)
    def exists(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Check if one or more keys exist
        redis_obj = self._pipe_to_redis(pipe)
        
        # Sometimes check multiple keys at once
        if random.random() < 0.4:
            additional_keys = []
            for _ in range(random.randint(1, 2)):
                extra_key = redis_obj.randomkey()
                if extra_key:
                    additional_keys.append(extra_key)
            
            if additional_keys:
                pipe.exists(key, *additional_keys)
            else:
                pipe.exists(key)
        else:
            pipe.exists(key)
    
    @cg_method("base", False)
    def type(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Get the data type of a key's value
        pipe.type(key)
    
    @cg_method("base", True)
    def rename(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Rename a key to a new name
        if random.random() < 0.8:
            new_key = self._rand_key("base")
        else:
            new_key = self._scan_rand_key(self._pipe_to_redis(pipe), "base") or key
        
        pipe.rename(key, new_key)
    
    @cg_method("base", False)
    def renamenx(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Rename key only if new name doesn't exist
        if random.random() < 0.8:
            new_key = self._rand_key("base")
        else:
            new_key = self._scan_rand_key(self._pipe_to_redis(pipe), "base") or key
        pipe.renamenx(key, new_key)
    
    @cg_method("base", False)
    def unlink(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Asynchronous key deletion (non-blocking)
        redis_obj = self._pipe_to_redis(pipe)
        
        # Sometimes unlink multiple keys at once
        if random.random() < 0.3:
            additional_keys = []
            for _ in range(random.randint(1, 3)):
                extra_key = redis_obj.randomkey()
                if extra_key:
                    additional_keys.append(extra_key)
            
            if additional_keys:
                pipe.unlink(key, *additional_keys)
            else:
                pipe.unlink(key)
        else:
            pipe.unlink(key)
    
    @cg_method("base", False)
    def touch(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Update last access time of keys
        redis_obj = self._pipe_to_redis(pipe)
        
        # Sometimes touch multiple keys at once
        if random.random() < 0.4:
            additional_keys = []
            for _ in range(random.randint(1, 2)):
                extra_key = redis_obj.randomkey()
                if extra_key:
                    additional_keys.append(extra_key)
            
            if additional_keys:
                pipe.touch(key, *additional_keys)
            else:
                pipe.touch(key)
        else:
            pipe.touch(key)
    
    @cg_method("base", True)
    def copy(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Copy key to new name with options
        dest_key = self._rand_key("base")
        
        kwargs = {}
        # Sometimes copy to different database
        if random.random() < 0.2:
            kwargs['destination_db'] = random.randint(1, 15)
        
        # Sometimes replace existing destination
        if random.random() < 0.3:
            kwargs['replace'] = True
        
        pipe.copy(key, dest_key, **kwargs)
    
    @cg_method("base", False)
    def move(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Move key to different Redis database
        db_number = random.randint(1, 15)
        pipe.move(key, db_number)
    
    @cg_method("base", False)
    def dump(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Serialize key value for backup/migration
        pipe.dump(key)
    
    @cg_method("base", True)
    def restore(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Restore key from serialized value
        # Note: This is a simplified version - in real usage you'd need actual dump data
        redis_obj = self._pipe_to_redis(pipe)
        
        # Try to get dump data from an existing key
        source_key = redis_obj.randomkey()
        if source_key:
            try:
                dump_data = redis_obj.dump(source_key)
                # Validate dump data exists and is properly formatted
                if dump_data and isinstance(dump_data, bytes) and len(dump_data) > 10:
                    ttl = random.randint(self.ttl_low, self.ttl_high)  
                    
                    kwargs = {}
                    if random.random() < 0.3:
                        kwargs['replace'] = True
                    if random.random() < 0.2:
                        kwargs['absttl'] = True
                    if random.random() < 0.2:
                        kwargs['idletime'] = random.randint(1, 1000)
                    if random.random() < 0.2:
                        kwargs['frequency'] = random.randint(1, 255)
                    
                    pipe.restore(key, ttl, dump_data, **kwargs)
                    return
            except (redis.exceptions.ResponseError, redis.exceptions.DataError, TypeError, AttributeError):
                # Skip on any Redis errors, data corruption, or type issues
                pass
        
        # Skip if we can't get valid dump data
        return
    
    @cg_method("base", False)
    def randomkey(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Get random key from database (key parameter ignored for this command)
        pipe.randomkey()
    
    @cg_method("base", False)
    def keys(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Find keys matching pattern (use carefully in production)
        patterns = [
            "*",
            f"{self.def_key_pref}*",
            "string:*",
            "list:*", 
            "set:*",
            "zset:*",
            "hash:*",
            "*:*",
            f"*{self._rand_str(3)}*"
        ]
        pattern = random.choice(patterns)
        pipe.keys(pattern)

if __name__ == "__main__":
    base_gen = parse(BaseGen)
    base_gen.distributions = '{"expire": 100, "pexpire": 80, "expireat": 60, "pexpireat": 50, "persist": 100, "ttl": 70, "pttl": 60, "expiretime": 40, "pexpiretime": 30, "delete": 90, "exists": 80, "type": 60, "rename": 40, "renamenx": 30, "unlink": 50, "touch": 40, "copy": 30, "move": 25, "dump": 20, "restore": 15, "randomkey": 35, "keys": 25}'
    base_gen._run()