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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from time import sleep

from cps_deckenmalerei.record import Record

def main():
    ##################################################################
    # CLASS TEST AND DEBUG
    #
    pass

class Snarf:
    ##################################################################
    # OBJECT PROPERTIES
    #
    properties = None

    ##################################################################
    # OBJECT PHOTOGRAPHS
    #
    photographs = None

    ##################################################################
    # PHOTO SLIDESHOW
    #
    _slider_parent = None
    _slider_nav = None

    ##################################################################
    # TMPDIR
    #
    _tmpdir = None

    ##################################################################
    # CHROME WEB DRIVER
    #
    _driver = None

    ##################################################################
    # akamaitechnologies hangs unless it recognises the User-Agent
    #
    _USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134."

    def __init__(self, url=None, wantphotos=True):
        self._tmpdir = tempfile.TemporaryDirectory(prefix="cps_deckenmalerei.tmp.")
        os.environ["TMPDIR"] = self._tmpdir.name
        if url:
            self.scrape(url, wantphotos)

    def __del__(self):
        self._tmpdir.cleanup()

    def scrape(self, url, wantphotos=True):
        while True:
            try:
                self._scrape(url, wantphotos)
                break

            except: # server timeout or error else driver session error
                if self._driver:
                    self._driver.quit()
                    self._driver = None
                sleep(5)

        self._driver.quit()
        self._driver = None

    def _scrape(self, url, wantphotos):
        ##################################################################
        # Chrome driver options
        #
        options = Options()
        options.add_argument("--incognito")
        options.add_argument("--headless")
        options.add_argument(f"user-agent={self._USER_AGENT}")
        # Do not load images
        prefs = { "profile.managed_default_content_settings.images": 2 }
        options.add_experimental_option("prefs", prefs)

        ##################################################################
        # Get URL
        #
        self._driver = webdriver.Chrome(options=options)
        self._driver.get(url)

        # Wait for page load else timeout
        WebDriverWait(self._driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@class='dataPage']")))

        # Scroll to end
        scroll = True
        while scroll:
            old_height = self._driver.execute_script("return document.body.scrollHeight;")
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_height = self._driver.execute_script("return document.body.scrollHeight;")
            scroll = new_height != old_height

        # Accept cookies
        button = WebDriverWait(self._driver, 60).until(EC.element_to_be_clickable((By.ID, "rcc-confirm-button")))
        self._driver.execute_script("arguments[0].click();", button)

        # Scroll to beginning
        self._driver.execute_script("window.scrollTo(0, 0);")

        ##################################################################
        # Extract properties
        #
        self.properties = {} # DICT OF LIST

        rows = self._driver.find_elements(by=By.XPATH, value="//div[@class='divTableRow']")
        for row in rows:
            var, text = Snarf.getvar(row.text)
            if text:
                if var == "TYP":
                    _url = url
                else:
                    _url = None
                    elements = row.find_elements(by=By.XPATH, value=".//a[@href]")
                    for element in elements:
                        if not _url:
                            _url = element.get_attribute("href")
                        else:
                            _url = _url + " " + element.get_attribute("href")
                if var not in self.properties:
                    self.properties[var] = [Record(text, _url)]
                else:
                    self.properties[var].append(Record(text, _url))

        ##################################################################
        # Extract any photographs
        #
        self.photographs = [] # LIST OF DICT

        try:
            self._slider_parent = self._driver.find_element(by=By.XPATH, value="//div[contains(@class, 'react__slick__slider__parent')]")
        except:
            wantphotos = False # NO PHOTOS PRESENT

        if wantphotos:
            elements = self._slider_parent.find_elements(by=By.XPATH, value=".//div[contains(@class, 'slick-slide') and @data-index]")
            count = len(elements)

            if count == 1:
                self.photographs.append(self._photo(0))
            elif count > 1: # PHOTO SLIDESHOW
                for i in range(1, count):
                    button = WebDriverWait(self._slider_parent, 60).until(EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class, 'slick-next')]")))
                    active = f".//div[@class='slick-slide slick-active slick-current' and @data-index='{i}']"
                    while True:
                        try:
                            # NB `Next' button click is problematic
                            self._driver.execute_script("arguments[0].click();", button)
                            sleep(0.5)
                            WebDriverWait(self._slider_parent, 0.5).until(EC.presence_of_element_located((By.XPATH, active)))
                            break
                        except:
                            pass
                self._slider_nav = self._driver.find_element(by=By.XPATH, value="//div[contains(@class, 'react__slick__slider__nav')]")
                for i in range(0, count):
                    self.photographs.append(self._photo(i))

    def _photo(self, index):
        ##################################################################
        # Extract image source
        #
        slide = self._slider_parent.find_element(by=By.XPATH, value=f".//div[contains(@class, 'slick-slide') and @data-index='{index}']")
        image = slide.find_element(by=By.XPATH, value=".//img[contains(@class, 'img-fluid')]")
        src = image.get_attribute("src")
        if not src and self._slider_nav:
            nav = self._slider_nav.find_element(by=By.XPATH, value=f".//div[contains(@class, 'slick-slide') and @data-index='{index}']")
            image = nav.find_element(by=By.XPATH, value=".//img[contains(@class, 'img-fluid')]")
            src = image.get_attribute("src")
        if not src:
            src = "404"
        elif src.endswith("b.jpg"):
            src = src[:-5] + "a.jpg"
        elif src.endswith("small"):
            src = src[:-5] + "preview"

        ##################################################################
        # Extract properties
        #
        properties = {}

        properties["TYP"] = Record("Foto", src)

        div = slide.find_element(by=By.XPATH, value=".//div[@class='']")
        rows = div.find_elements(by=By.XPATH, value=".//div")
        for row in rows:
            try:
                element = row.find_element(by=By.XPATH, value=".//a[@href]")
                url = element.get_attribute("href")
            except:
                url = None
                pass
            soup = BeautifulSoup(row.get_attribute("innerHTML"), "html.parser")
            var, text = Snarf.getvar(soup.text)
            if text:
                properties[var] = Record(text, url)

        return properties

    def hat_teil(self, wanttype=False):
        parts = []
        for property in self.properties:
            if property == "HAT TEIL":
                for record in self.properties[property]:
                    typ = Snarf.gettype(record.text)
                    if typ:
                        if wanttype == typ or wanttype == False:
                            parts.append(Record(typ, record.url))
        return parts

    @staticmethod
    def getvar(s):
        s = s.replace('\n', ' ')
        s = s.strip()
        a = s.split(':', maxsplit=1)
        if len(a) > 1:
            return a[0].strip().upper(), a[1].strip()
        return s, None

    @staticmethod
    def gettype(s):
        l = s.rindex('[')
        r = s.rindex(']')
        if r == len(s) - 1:
            return s[1 + l:r].strip()
        return None

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
