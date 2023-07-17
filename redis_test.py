import time
import redis

class RedisClient:
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.sub = None 

    def set_key(self, key, value):
        self.r.set(key, value)
        
    def get_value(self, key):
        value = self.r.get(key)
        if value is not None:
            value = value.decode('utf-8')
        return value
        
    def increment_counter(self, key):
        self.r.incr(key)
        
    def decrement_counter(self, key):
        self.r.decr(key)
        
    def delete_key(self, key):
        self.r.delete(key)

    def no_sessions(self):
        self.delete_key(f"simulator:sessions")

    def create_sessions(self, count):
        self.set_key(f"simulator:sessions", count)
        
    def create_state(self, user_id):
        self.r.hmset(f"user:{user_id}:simulator", {"state_data": "value1", "state_data2": "value2"})

    def add_set(self, set_name, set_value):
        self.r.sadd(set_name, set_value)
    
    def add_hash_value(self, step_value, step_attribute, hashfield, hashvalue):
        self.r.hset(f'simulator:1:{step_attribute}:{step_value}', hashfield, hashvalue)
    
    def get_hash_value(self, step_id):
        val = self.r.hget(f'simulator:1:step_id:{step_id}','complete')
        return val

    def prerequisite(self, user_id, step_val):
        self.r.sadd(f'simulator:{user_id}:step_ids', step_val)
        self.r.hset(f'simulator:{user_id}:step_name:{step_val}', 'complete', '1')
        self.r.hset(f'simulator:{user_id}:step_id:{step_val}', 'complete', '1')

    def subscribe(self):
        self.sub = self.r.pubsub()
        self.sub.subscribe("api-requests")
        return True

    def listen(self):
        start = time.time()
        for message in self.sub.listen():
            if message and message['type'] != 'subscribe':
                _token = message['data']
                break
            now = time.time()
            if now - start > 10:
                _token = ""
                break
        self.sub.unsubscribe()

        _message = self.r.hgetall(f'request:{_token}')
        return _message

# redis_client = RedisClient()
# redis_client.set_key('mykey', 'myvalue')
# value = redis_client.get_value('mykey')
# print(value) # This will output 'myvalue'
# redis_client.increment_counter('mycounter')
# redis_client.delete_key('mykey')
