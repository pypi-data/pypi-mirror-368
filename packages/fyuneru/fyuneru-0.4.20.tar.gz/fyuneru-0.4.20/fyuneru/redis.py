from fyuneru.lib import hash


def generate_redis_key(task_name: str, user_name: str = "inklov3"):
    return f"{task_name}:{user_name}"
