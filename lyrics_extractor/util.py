def fail_retry(limit=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            local_limit = limit
            last_exception = None
            while local_limit:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print('---Retrying...')
                    last_exception = e
                local_limit -= 1
            return f"ERROR\n{repr(last_exception)}"

        return wrapper

    return decorator
