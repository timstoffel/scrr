#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Main Method for Docker Hub Scraper

import requests
from module_logging import Logger
#import csv
from writefile import writefile
#import string
import json
#from urllib.request import urlopen
#from pathlib import Path

class docker_hub_scraper():
    def __init__(self, logger):
        self.logger = logger

    def loop(self):
        payload = {}

        for i in range(1,18):
            payload["page"] = str(i)
            self.parsePage(payload)

    def parsePage(self, payload):

        url = "https://hub.docker.com/v2/repositories/library/"

        headers = {
            'User-Agent': "PostmanRuntime/7.20.1",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "565710ab-779b-42f8-bfec-9cd708ea232e,be669230-53d6-4893-9e34-83e58e7ce57d",
            'Host': "hub.docker.com",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
            }

        response = requests.request("GET", url, headers=headers, params=payload)


        json_obj = json.loads(response.text)

        for member in json_obj['results']:
 
            try:
                name = member['name']
            except:
                name = ""

            try:
                pull_count = member['pull_count']
            except:
                pull_count = ""

            try: 
                star_count = member['star_count']
            except:
                star_count= ""

            writefile.writecsv(None, 'docker', [name, pull_count, star_count])


    def run(self):
        self.logger.info("Start docker hub Scraper.")
        self.loop()

def main():
    logger = Logger().init_logging()
    #writefile()
    try:
        writefile.writecsv(None, 'docker', ['name', 'pull_count', 'star_count'])
        scraper = docker_hub_scraper(logger)
        scraper.run()

    except Exception as e:
        logger.exception(e)

if __name__ == '__main__':
    main()
