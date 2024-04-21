import requests

url = "https://www.linkedin.com/jobs/view/3900673172/?eBP=NON_CHARGEABLE_CHANNEL&refId=i04y11%2FYD%2FYrzwHVJfx0qA%3D%3D&trackingId=b%2B%2FFdJoNBPtRaDtjdEwbcw%3D%3D&trk=flagship3_search_srp_jobs"

# Make requests
response = requests.get(url)
print(response.text)

# Function to fetch list of proxies from the API
def fetch_proxies():
    url = "https://www.proxy-list.download/api/v1/get?type=https"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.split("\r\n")  # Split the response text into a list of proxies
    else:
        return []
# Define rotating proxies
proxies = fetch_proxies()

import random
import requests

def scraping_request(url):

   ip = random.randrange(0, len(proxies))

   ips = {"http": proxies[ip], "https": proxies[ip]}
   response = requests.get(url, proxies=ips)
   print(f"Proxy currently being used: {ips['https']}")
   return response.text