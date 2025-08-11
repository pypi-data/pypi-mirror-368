#! /usr/bin/env python3
#
# Copyright (C) 2025 The Authors
# All rights reserved.
#
# This file is part of cps_deckenmalerei.
#
# cps_deckenmalerei is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# cps_deckenmalerei is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with cps_deckenmalerei. If not, see http://www.gnu.org/licenses/
#
import argparse
import os
import tempfile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# akamaitechnologies hangs unless it recognises the User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134."

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("file", type=str, help="file")

    args = parser.parse_args()

    tmpdir = tempfile.TemporaryDirectory(prefix="cps_deckenmalerei.tmp.")
    os.environ["TMPDIR"] = tmpdir.name

    urls = scrape("https://www.deckenmalerei.eu/texte-bundesland")

    print(f"\nFILE = {args.file}")
    with open(args.file, "w", encoding="utf-8") as f:

        for url in sorted(urls):
            f.write(url)
            f.write('\n')

    tmpdir.cleanup()

def scrape(url):
    print(f"\nURL = {url}")

    ##################################################################
    # Chrome driver options
    #
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    options.add_argument(f"user-agent={USER_AGENT}")
    # Do not load images
    prefs = { "profile.managed_default_content_settings.images": 2 }
    options.add_experimental_option("prefs", prefs)

    ##################################################################
    # Get URL
    #
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(60)
    driver.get(url)

    # Wait for page load
    driver.find_element(By.XPATH, value="//div[@class='entityListsPage']")

    # Scroll to end
    scroll = True
    while scroll:
        old_height = driver.execute_script("return document.body.scrollHeight;")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight;")
        scroll = new_height != old_height

    ##################################################################
    # Extract URLs
    #
    elements = driver.find_elements(by=By.XPATH, value="//div[@class='itemFooter']")

    urls = set()

    for element in elements:
        anchor = element.find_element(by=By.XPATH, value=".//a[@href]")
        urls.add(anchor.get_attribute("href"))

    driver.quit()

    print(f"URLS = {len(urls)}")

    return urls

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
