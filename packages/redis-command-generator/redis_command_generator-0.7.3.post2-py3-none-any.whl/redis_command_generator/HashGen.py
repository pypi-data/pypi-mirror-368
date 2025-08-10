import redis
import random
import time
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen, cg_method
from redis.commands.core import HashDataPersistOptions

@dataclass
class HashGen(BaseGen):
    max_subelements: int = 10
    subkey_size: int = 5
    subval_size: int = 5
    incrby_min: int = -1000
    incrby_max: int = 1000
    
    @cg_method(cmd_type="hash", can_create_key=True)
    def hset(self, pipe: redis.client.Pipeline, key: str) -> None:
        fields = {self._rand_str(self.subkey_size): self._rand_str(self.subval_size) for _ in range(random.randint(1, self.max_subelements))}
        pipe.hset(key, mapping=fields)
    
    @cg_method(cmd_type="hash", can_create_key=True)
    def hincrby(self, pipe: redis.client.Pipeline, key: str) -> None:
        field = self._rand_str(self.def_key_size)
        increment = random.randint(self.incrby_min, self.incrby_max)
        pipe.hincrby(key, field, increment)
    
    @cg_method(cmd_type="hash", can_create_key=True)
    def hincrbyfloat(self, pipe: redis.client.Pipeline, key: str) -> None:
        field = self._rand_str(self.subkey_size)
        increment = random.uniform(self.incrby_min, self.incrby_max)
        pipe.hincrbyfloat(key, field, increment)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hdel(self, pipe: redis.client.Pipeline, key: str) -> None:
        fields = [self._rand_str(self.subkey_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.hdel(key, *fields)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hgetdel(self, pipe: redis.client.Pipeline, key: str) -> None:
        redis_obj = self._pipe_to_redis(pipe)
        fields = redis_obj.hkeys(key)
        pipe.hgetdel(key, *fields)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hgetex(self, pipe: redis.client.Pipeline, key: str) -> None:
        redis_obj = self._pipe_to_redis(pipe)
        fields = redis_obj.hkeys(key)
        
        # Choose a random expiry option
        expiry_option = random.choice(['EX', 'PX', 'EXAT', 'PXAT', 'PERSIST'])
        
        # Prepare keyword arguments for expiry options
        kwargs = {}
        if expiry_option == 'EX':
            # Expire in seconds
            kwargs['ex'] = random.randint(self.ttl_low, self.ttl_high)
        elif expiry_option == 'PX':
            # Expire in milliseconds
            kwargs['px'] = random.randint(self.ttl_low * 1000, self.ttl_high * 1000)
        elif expiry_option == 'EXAT':
            # Expire at unix timestamp in seconds
            kwargs['exat'] = int(time.time()) + random.randint(self.ttl_low, self.ttl_high)
        elif expiry_option == 'PXAT':
            # Expire at unix timestamp in milliseconds
            kwargs['pxat'] = int(time.time() * 1000) + random.randint(self.ttl_low * 1000, self.ttl_high * 1000)
        elif expiry_option == 'PERSIST':
            kwargs['persist'] = True
        
        pipe.hgetex(key, *fields, **kwargs)
    
    @cg_method(cmd_type="hash", can_create_key=True)
    def hsetex(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Choose a random expiry option
        expiry_option = random.choice(['EX', 'PX', 'EXAT', 'PXAT', 'KEEPTTL'])
        
        # Prepare kwargs for the command
        kwargs = {}
        
        # Decide on optional flags (FNX, FXX)
        data_persist_option = random.choice([None, HashDataPersistOptions.FNX, HashDataPersistOptions.FXX])
        if data_persist_option:
            kwargs['data_persist_option'] = data_persist_option
        
        # Add expiry option
        if expiry_option == 'EX':
            # Expire in seconds
            kwargs['ex'] = random.randint(self.ttl_low, self.ttl_high)
        elif expiry_option == 'PX':
            # Expire in milliseconds
            kwargs['px'] = random.randint(self.ttl_low * 1000, self.ttl_high * 1000)
        elif expiry_option == 'EXAT':
            # Expire at unix timestamp in seconds
            kwargs['exat'] = int(time.time()) + random.randint(self.ttl_low, self.ttl_high)
        elif expiry_option == 'PXAT':
            # Expire at unix timestamp in milliseconds
            kwargs['pxat'] = int(time.time() * 1000) + random.randint(self.ttl_low * 1000, self.ttl_high * 1000)
        elif expiry_option == 'KEEPTTL':
            kwargs['keepttl'] = True
        
        items = []
        for _ in range(random.randint(1, self.max_subelements)):
            items.append(self._rand_str(self.subkey_size))  # Field
            items.append(self._rand_str(self.subval_size))  # Value
        pipe.hsetex(key, items=items, **kwargs)
    
    @cg_method(cmd_type="hash", can_create_key=True)
    def hsetnx(self, pipe: redis.client.Pipeline, key: str, existing_field_prob: float = 0.3) -> None:
        redis_obj = self._pipe_to_redis(pipe)
        fields = redis_obj.hkeys(key)
        use_existing = fields and random.random() < existing_field_prob
        if use_existing:
            field = random.choice(fields)
        else:
            field = self._rand_str(self.subkey_size)
        value = self._rand_str(self.subval_size)
        pipe.hsetnx(key, field, value)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hget(self, pipe: redis.client.Pipeline, key: str) -> None:
        redis_obj = self._pipe_to_redis(pipe)
        fields = redis_obj.hkeys(key)
        if fields:
            field = random.choice(fields)
        else:
            field = self._rand_str(self.subkey_size)
        pipe.hget(key, field)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hmget(self, pipe: redis.client.Pipeline, key: str) -> None:
        redis_obj = self._pipe_to_redis(pipe)
        fields = redis_obj.hkeys(key)
        if fields:
            num_fields = random.randint(1, min(len(fields), self.max_subelements))
            selected_fields = random.sample(fields, num_fields)
        else:
            selected_fields = [self._rand_str(self.subkey_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.hmget(key, selected_fields)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hexists(self, pipe: redis.client.Pipeline, key: str, existing_field_prob: float = 0.3) -> None:
        redis_obj = self._pipe_to_redis(pipe)
        fields = redis_obj.hkeys(key)
        use_existing = fields and random.random() < existing_field_prob
        if use_existing:
            field = random.choice(fields)
        else:
            field = self._rand_str(self.subkey_size)
        pipe.hexists(key, field)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hgetall(self, pipe: redis.client.Pipeline, key: str) -> None:
        pipe.hgetall(key)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hkeys(self, pipe: redis.client.Pipeline, key: str) -> None:
        pipe.hkeys(key)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hlen(self, pipe: redis.client.Pipeline, key: str) -> None:
        pipe.hlen(key)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hvals(self, pipe: redis.client.Pipeline, key: str) -> None:
        pipe.hvals(key)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hscan(self, pipe: redis.client.Pipeline, key: str) -> None:
        # Use a random cursor and optionally a match pattern
        cursor = random.randint(0, 1000)
        match = None
        if random.random() < 0.5:
            match = f"{self._rand_str(2)}*"
        count = random.randint(1, self.max_subelements)
        if match:
            pipe.hscan(key, cursor=cursor, match=match, count=count)
        else:
            pipe.hscan(key, cursor=cursor, count=count)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hrandfield(self, pipe: redis.client.Pipeline, key: str) -> None:
        count = None
        withvalues = False
        if random.random() < 0.5:
            count = random.randint(1, self.max_subelements)
        if random.random() < 0.5:
            withvalues = True
        if count is not None:
            pipe.hrandfield(key, count=count, withvalues=withvalues)
        else:
            pipe.hrandfield(key)
    
    @cg_method(cmd_type="hash", can_create_key=False)
    def hstrlen(self, pipe: redis.client.Pipeline, key: str) -> None:
        redis_obj = self._pipe_to_redis(pipe)
        fields = redis_obj.hkeys(key)
        if fields:
            field = random.choice(fields)
        else:
            field = self._rand_str(self.subkey_size)
        pipe.hstrlen(key, field)

if __name__ == "__main__":
    hash_gen = parse(HashGen)
    hash_gen.distributions = '{"hset": 100, "hincrby": 100, "hdel": 100, "hgetdel": 100, "hgetex": 100, "hsetex": 100, "hsetnx": 100}'
    hash_gen._run()
