import threading
import time
from functools import wraps


def with_timer():
    """
    Декоратор, отображающий счетчик времени выполнения функции в реальном времени.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            stop_counter = threading.Event()

            def display_timer():
                print("DEBUG: Счетчик запущен")
                start_time = time.time()
                while not stop_counter.is_set():
                    elapsed_time = time.time() - start_time
                    print(f"\rВремя выполнения: {elapsed_time:.2f} секунд", end='', flush=True)
                    time.sleep(0.1)
                print(f"\rDEBUG: Счетчик остановлен. Общее время: {time.time() - start_time:.2f} секунд")

            timer_thread = threading.Thread(target=display_timer, daemon=True)
            timer_thread.start()

            try:
                result = func(*args, **kwargs)
            finally:
                stop_counter.set()
                timer_thread.join()

            return result

        return wrapper

    return decorator
