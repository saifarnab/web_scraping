import requests
from itertools import cycle
import traceback

# Enter proxy ip's and ports in a list.
proxies = {
    'http://129.226.33.104:3218',
    'http://169.57.1.85:8123',
    'http://85.25.91.141:15333',
    'http://103.149.162.195:80',
    'http://8.218.213.95:10809'
}

proxy_pool = cycle(proxies)

# Initialize a URL.

url = 'https://httpbin.org/ip'  # Iterate through the proxies and check if it is working.
for i in range(1, 6):

    # Get a proxy from the pool

    proxy = next(proxy_pool)
    print("Request #%d" % i)
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=30)
        print(response.json())
    except:
        # Most free proxies will often get connection errors. You will need to retry the request using another proxy.
        print("Skipping. Connection error")
