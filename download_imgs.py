"""Script to download images from bing search api."""


from requests import exceptions
import requests
import cv2
import os
from secret_key import s


# set up for search api

api_key = s
max_results = 500
group_size = 50

url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

# collating exceptions that may occur during download process

EXCEPTIONS = set([
    IOError,
    exceptions.RequestException,
    exceptions.HTTPError,
    exceptions.ConnectionError,
    exceptions.Timeout
])

term = 'passport id samples'
headers = {"Ocp-Apim-Subscription-Key": api_key}
params = {"q": term, "offset": 0, "count": group_size}
output = 'data/'

print("Searching bing for '{}'".format(term))
search = requests.get(url, headers=headers, params=params)
search.raise_for_status()

results = search.json()
est_results = min(results['totalEstimatedMatches'], max_results)
print("{} total results for '{}'".format(est_results, term))

total = 0

for offset in range(0, est_results, group_size):
    print('making request for group {}-{} for {}...'.format(offset, offset + group_size, est_results))
    params['offset'] = offset
    search = requests.get(url, headers=headers, params=params)
    search.raise_for_status()
    results = search.json()
    print("Saving images for group {}-{} of {}...".format(offset, offset + group_size, est_results))
    for v in results["value"]:
        try:
            # fetching the images
            r = requests.get(v["contentUrl"], timeout=30)

            ext = v["contentUrl"][v["contentUrl"].rfind("."):]
            p = os.path.sep.join([output, "{}{}".format(str(total).zfill(8), ext)])

            with open(p, "wb") as f:
                f.write(r.content)

            try:
                image = cv2.imread(p)
                if image is None:
                    os.remove(p)
                    continue
                total += 1
            except Exception as e:
                os.remove(p)
        except Exception as e:
            if type(e) in EXCEPTIONS:
                continue
