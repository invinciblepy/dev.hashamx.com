import requests
import random
import time
from requests.exceptions import RequestException, Timeout, ConnectionError, ChunkedEncodingError, TooManyRedirects, HTTPError

def fetch_url(url, params=None, headers=None, retries=3, timeout=10):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                print(f"[!] Non-JSON response on attempt {attempt+1}")
        except (RequestException, Timeout, ConnectionError, ChunkedEncodingError, TooManyRedirects, HTTPError) as e:
            print(f"[!] Request failed on attempt {attempt+1}: {e}")
        attempt += 1
        sleep_time = random.uniform(1, 3)
        print(f"[*] Retrying in {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
    raise Exception(f"[x] Failed after {retries} attempts.")
