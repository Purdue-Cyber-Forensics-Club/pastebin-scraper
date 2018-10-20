#!/usr/bin/python3
# This above line is to tell Unix-based systems that this file is executed with
# Python3. This allows us to run `./main.py` in the terminal instead of
# `python3 main.py` everytime.

"""
This module is a simple Pastebin web scraper that searches and stores pastes
containing a set of keywords.
"""

# These are the modules we are importing from the packages we installed via
# `pip install --user bs4`, for example.
import time
import gzip
import re
import json
from io import StringIO
import urllib.request
import urllib.error
from bs4 import BeautifulSoup as bs

# A list of global variables to be referenced later.
URL_ROOT = "http://pastebin.com/"
URL_RAW = URL_ROOT + "raw/"  # An example of concatenation.
KEYWORDS = [
    {
        "category": "Top 20 Passwords",
        "word": "(1234(5|56|567|5678)?|password|pussy|dragon|qwerty|696969|mustang|baseball|football|letmein|monkey|abc123|michael|shadow|master|jennifer|111111)",
        "count": 0,
        "sources": [],
    },
    {
        "category": "Email Address",
        "word": "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "count": 0,
        "sources": [],
    },
    {
        "category": "IPv4 Address",
        "word": "(?:[0-9]{1,3}\.){3}[0-9]{1,3}",
        "count": 0,
        "sources": [],
    },
    {
        "category": "US Phone Number",
        "word": "(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?",
        "count": 0,
        "sources": [],
    },
    {
        "category": "UUID",
        "word": "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89AB][0-9a-f]{3}-[0-9a-f]{12}",
        "count": 0,
        "sources": [],
    },
    {
        "category": "(Google) API Keys",
        "word": "(api|key).*[A-Za-z0-9]{39,40}",
        "count": 0,
        "sources": [],
    },
]
PASTE_CACHE = set([])
REGEX_CACHE = {}
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"


def parse_paste(paste_url):
    """
    Parses content in search of relevant text and updates the keywords data
    structure accordingly.
    """
    print("Scraping", paste_url, "...")
    content = fetch_html(paste_url)
    hits_on_page = 0
    for keyword in KEYWORDS:
        # Since regexes are expensive to compile, let's cache them.
        if keyword["word"] in REGEX_CACHE:
            regex = REGEX_CACHE[keyword["word"]]
        else:
            REGEX_CACHE[keyword["word"]] = re.compile(
                keyword["word"], re.IGNORECASE | re.MULTILINE
            )
            regex = REGEX_CACHE[keyword["word"]]
        results = regex.findall(content)
        if results:
            keyword["count"] += len(results)
            hits_on_page += len(results)
            keyword["sources"].append([paste_url, len(results)])
    if hits_on_page:
        print(" > Discovered", hits_on_page, "hits")
    return hits_on_page


def save_results():
    """Take scrape results and store them into a JSON file."""
    print("Saving to disk ...")
    file_desc = open("scrape_results.json", "w")
    json.dump(KEYWORDS, file_desc, indent=4, sort_keys=True)


def fetch_html(url):
    """
    Download the webpage given at the URL, unzip it if necessary, then return it
    as searchable HTML.
    """
    # Form a request with a user agent that makes us not look like a script.
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    response = urllib.request.urlopen(request)

    if response.info().get("Content-Encoding") == "gzip":
        response_buffer = StringIO(response.read())
        unzipped = gzip.GzipFile(fileobj=response_buffer)
        return unzipped.read().decode("utf-8")
    return response.read().decode("utf-8")


def get_latest_pastes():
    """Fetch the URL's of the latest pastes from the front page."""
    print("Fetching latest ...")
    discovered_links = []
    # Have Beautiful Soup parse the HTML so we can navigate it easier.
    front_page = bs(fetch_html(URL_ROOT), "html.parser")
    right_menu = front_page.find("div", {"id": "menu_2"})
    right_menu_list = right_menu.find("ul", {"class": "right_menu"})
    for item in right_menu_list.findChildren():
        if item.find("a"):
            # Find and store all the links from the sidebar of the front page.
            discovered_links.append(str(item.find("a").get("href")).replace("/", ""))
    return discovered_links


def main():
    """Begins the scraping loop."""
    try:
        while True:
            latest = get_latest_pastes()
            set_updated = False
            for paste in latest:
                original_size = len(PASTE_CACHE)
                PASTE_CACHE.add(paste)
                if len(PASTE_CACHE) > original_size:
                    set_updated = True
                    paste_url = URL_RAW + paste
                    hits = parse_paste(paste_url)
            if not set_updated:
                print("No updates, sleeping ...")
                time.sleep(10)
            else:
                time.sleep(5)
            save_results()
            print("Saving ...")
    except KeyboardInterrupt:
        save_results()
        print("Exiting ...")
    except urllib.error.HTTPError:
        print("An HTTP error occurred.")


# Kick off the program.
main()
