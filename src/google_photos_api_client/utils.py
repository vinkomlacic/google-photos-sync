import functools


def log_api_call(logger):
    """Wraps calls to the API and logs what function was called.

    Note: this only works on class methods, not on functions.
    """

    def log_api_call_wrapper(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Using the self argument to access the class name
            class_name = args[0].__class__.__name__
            logger.info(f'{class_name}: Calling method {func.__name__}.')

            return_value = func(*args, **kwargs)

            logger.info(f'{class_name}: Method {func.__name__} successfully returned.')

            return return_value

        return wrapper

    return log_api_call_wrapper
