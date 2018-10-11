#!/usr/bin/python3
# This above line is to tell Unix-based systems that this file is executed with
# Python3. This allows us to run `./main.py` in the terminal instead of
# `python3 main.py` everytime.

# These are the modules we are importing from the packages we installed via
# `pip install --user bs4`, for example.
import time
import gzip
import urllib3 as URL
import json
from bs4 import BeautifulSoup as bs
from io import StringIO

http = URL.PoolManager()

# A list of global variables to be referenced later.
urlRoot = "http://pastebin.com/"
urlRaw = urlRoot + "raw/" # An example of concatenation.
keywords = [
    {"word": "password", "count": 0, "sources": [] },
    {"word": "email", "count": 0, "sources": [] },
    {"word": "username", "count": 0, "sources": [] },
    {"word": "database", "count": 0, "sources": [] },
    {"word": "crack", "count": 0, "sources": [] },
    {"word": "hack", "count": 0, "sources": [] },
    {"word": "security", "count": 0, "sources": [] },
    {"word": "purdue", "count": 0, "sources": [] }
]
pasteCache = set([])

# Makes a single web request to Pastebin and parse its
# content for relevant text.
def scrape():
    print("Scraping ...")
    return parse("The quick brown fox jumped over the lazy dog.")

# Parses content in search of relevant text and updates the keywords data
# structure accordingly.
def parsePaste(pasteUrl):
    content = fetchHtml(pasteUrl)
    hitsOnPage = 0
    for keyword in keywords:
        results = content.find_all(keyword["word"], limit = 100)
        if len(results) > 0:
            keyword["count"] += len(results)
            hitsOnPage += len(results)
            keyword["sources"].append(pasteUrl)
    return hitsOnPage

# Take scrape results and store them into a JSON file.
def saveResults():
    file = open("scrapeResults.json", "w")
    json.dump(keywords, file)

# Download the webpage given at the URL, unzip it if necessary, then return it
# as searchable HTML.
def fetchHtml(url):
    # response = URL.urlopen(url)
    response = http.request("GET", url)
    if response.info().get("Content-Encoding") == "gzip":
        buffer = StringIO(response.read())
        unzipped = gzip.GzipFile(fileobj = buffer)
        return unzipped.read()
    else:
        return response.read()

# Fetch the URL's of the latest pastes from the front page.
def getLatestPastes():
    discoveredLinks = []
    frontPage = fetchHtml(urlRoot)
    rightMenu = frontPage.find("div", {"id": "menu_2"})
    rightMenuList = rightMenu.find("ul", {"class": "right_menu"})
    for item in rightMenuList.findChildren():
        if item.find("a"):
            discoveredLinks.append(
                str(item.find("a").get("href")).replace("/", ""))
    return discoveredLinks

# Begins the scraping loop.
def main():
    try:
        while True:
            print("Checking ...")
            latest = getLatestPastes()
            for paste in latest:
                originalSize = len(pasteCache)
                pasteCache.add(paste)
                if len(pasteCache) > originalSize:
                    pasteUrl = urlRaw + paste
                    hits = parsePaste(pasteUrl)
                    if hits > 0:
                        print(hits, "hits on", pasteUrl, "!")
                else:
                    time.sleep(3)
    except KeyboardInterrupt:
        saveResults()
        print("Exiting ...")
    except URL.exceptions.HTTPError:
        print("An HTTP error occurred")
    print("Returned", scrape())

# Kick off the program.
main()
