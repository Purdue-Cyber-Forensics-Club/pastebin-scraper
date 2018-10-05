#!/usr/bin/python3
# This above line is to tell Unix-based systems that this file is executed with
# Python3. This allows us to run `./main.py` in the terminal instead of
# `python3 main.py` everytime.

# These are the modules we are importing from the packages we installed via
# `pip install --user bs4`, for example.
import time
from bs4 import BeautifulSoup as bs

# Makes a single web request to Pastebin and parse its
# content for relevant text.
def scrape():
    print("Scraping ...")
    return parse("The quick brown fox jumped over the lazy dog.")

# Parses content in search of relevant text; returns true if relevant, false
# otherwise.
def parse(content):
    print("Parsing string ...")
    return True

# Begins the scraping loop.
def main():
    print("Hello, world!")
    print("Returned", scrape())

# Kick off the program.
main()
