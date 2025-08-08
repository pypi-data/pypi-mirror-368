import threading

from .core_exceptions import SincproNoResultFound, SincproTimeoutException


# TIMEOUT DECORATOR
class InterruptableThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._result = None

    def run(self):
        self._result = self._func(*self._args, **self._kwargs)

    @property
    def result(self):
        return self._result


# -------------------------------------------------------------------------------------------------------
# Timeout for Sync Object
# -------------------------------------------------------------------------------------------------------
class timeout(object):
    def __init__(self, sec):
        self._sec = sec

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            it = InterruptableThread(f, *args, **kwargs)
            it.start()
            it.join(self._sec)
            if not it.is_alive():
                if it.result is None:
                    raise FileNotFoundError("The Sync object was not able to found")
                return it.result
            raise SincproTimeoutException("execution expired")

        return wrapped_f


class timeout_with_check_exists_response(object):
    def __init__(self, timeout_in_seconds):
        self._sec = timeout_in_seconds

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            it = InterruptableThread(f, *args, **kwargs)
            it.start()
            it.join(self._sec)
            if not it.is_alive():
                if it.result is None:
                    raise SincproNoResultFound(
                        f"There is no value result for the execution [{f.__name__}]"
                    )
                return it.result
            raise SincproTimeoutException("execution expired")

        return wrapped_f
