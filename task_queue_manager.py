import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

class TaskQueueManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskQueueManager, cls).__new__(cls)
            REDIS_URL = os.getenv("REDIS_URL")
            if not REDIS_URL:
                raise ValueError("REDIS_URL environment variable not set.")
            cls._instance.redis_client = redis.from_url(REDIS_URL)
            cls._instance.queue_name = "task_queue"
        return cls._instance

    def push_task(self, task):
        """Pushes a task onto the Redis queue."""
        try:
            self.redis_client.rpush(self.queue_name, json.dumps(task))
            print(f"Pushed task to queue: {task}")
        except redis.exceptions.RedisError as e:
            print(f"Error pushing task to Redis: {e}")

    def pull_task(self):
        """Pulls a task from the Redis queue. This is a blocking operation."""
        try:
            _, task_json = self.redis_client.blpop(self.queue_name)
            task = json.loads(task_json)
            print(f"Pulled task from queue: {task}")
            return task
        except redis.exceptions.RedisError as e:
            print(f"Error pulling task from Redis: {e}")
            return None
        except TypeError:
             # This can happen if blpop returns None during a shutdown
            return None

    def get_queue_size(self):
        """Gets the current size of the task queue."""
        try:
            return self.redis_client.llen(self.queue_name)
        except redis.exceptions.RedisError as e:
            print(f"Error getting queue size from Redis: {e}")
            return 0

# Singleton instance
task_queue = TaskQueueManager()

# Expose functions for easy import
def push_task(task):
    task_queue.push_task(task)

def pull_task():
    return task_queue.pull_task()

def get_queue_size():
    return task_queue.get_queue_size()
