import functools
import time
import requests
from requests.exceptions import RequestException


def retry_on_failure(max_retries=3, delay=2, backoff=2, allowed_statuses=(429, 500, 502, 503, 504)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    response = func(*args, **kwargs)
                    if isinstance(response, requests.Response):
                        if response.status_code in allowed_statuses:
                            print(f"[Retry {retries + 1}] HTTP {response.status_code} — Retrying after {current_delay}s")
                        else:
                            return response
                    else:
                        return response
                except RequestException as e:
                    print(f"[Retry {retries + 1}] Exception: {e} — Retrying after {current_delay}s")
                time.sleep(current_delay)
                retries += 1
                current_delay *= backoff
            raise Exception(f"Function `{func.__name__}` failed after {max_retries} retries")
        return wrapper
    return decorator

@retry_on_failure()
def fetch_url(url, headers=None):
    return requests.get(url, headers=headers, timeout=10)

@retry_on_failure()
def post_form(url, data, headers=None):
    return requests.post(url, data=data, headers=headers, timeout=10)

@retry_on_failure()
def post_multipart(url, files, headers=None):
    return requests.post(url, files=files, headers=headers, timeout=10)

@retry_on_failure()
def post_any(url, headers=None, **kwargs):
    return requests.post(url, headers=headers, timeout=10, **kwargs)