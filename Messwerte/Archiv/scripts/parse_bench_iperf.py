
import zipfile
import json
import os
import math
import json
import logging
import re
import sys
import argparse
import csv
from logging.handlers import RotatingFileHandler
from io import StringIO
from pathlib import Path  

logger = logging.getLogger()
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
log_handler.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)    


# Parser helper
class TimeBenchResult:

    def __init__(self, path):
        self.filepath = path
        self.send = -1.0
        self.received = -1.0
        self.ressource_limit = ""
        self.runtime = ""
        self.image_name = ""
        self.repeat = ""
        self.duration = ""
        self.type = ""
        
    def __str__(self):
        return self.filepath

    def readInformationFromFile(self):

        try: 
            textfile = open(self.filepath, 'r')
            filetext = textfile.read()
            textfile.close()
        except Exception:
            logger.error("Opening of file failed: " + self.filepath,  exc_info=True) 

        try:
            json_obj = json.loads(filetext)

            if 'tcp' in self.filepath:
                self.send = json_obj['end']['sum_sent']['bits_per_second']
                self.received = json_obj['end']['sum_received']['bits_per_second']
                self.type = "tcp"

            elif 'udp' in self.filepath:
                self.send = json_obj['end']['sum']['bits_per_second']
                self.received = -1.0
                self.type = "udp"

            else:
                logger.error("Parsing error in: " + self.filepath,  exc_info=True) 
        except Exception:
            logger.error("Parsing error in: " + self.filepath,  exc_info=True) 

    def readInformationFromPath(self, basePath):

        workingPath = self.filepath.replace(basePath, '')
        pathParts = workingPath.split('/')

        try: 
            if len(pathParts) == 6:
                self.ressource_limit = pathParts[0]
                self.runtime = pathParts[1]
                self.image_name = pathParts[2]
                self.duration = pathParts[3]
                self.repeat = pathParts[4].replace('repeat_', '')
            else:
                logger.error("Parsing error not six arguments in: " + self.filepath)
        except Exception:
            logger.error("Parsing Exception in: " + self.filepath,  exc_info=True)

def getListOfFiles(path):

    listOfFile = os.listdir(path)
    allFiles = list()

    try: 
        for entry in listOfFile:
            fullPath = os.path.join(path, entry)
            if os.path.isdir(fullPath):
                allFiles = allFiles + getListOfFiles(fullPath)
            else:
                allFiles.append(fullPath)
    except Exception:
        logger.error("Can't get File List",  exc_info=True)
                
    return allFiles

def main():

    parser = argparse.ArgumentParser(description='Parser for ApacheBench Results from Ansible Role')
    # parser.add_argument("--path", required=True, help="Input Path")

    parser.add_argument("--path", default="C:\\Work\\Bachelorarbeit\\Auswertung\\Raw\\bench_iperf_vagrant\\", help="Input Path")
    parser.add_argument("--export", default="export_iperf.csv", help="Export Path")

    args = parser.parse_args()

    if args.export == "export_iperf.csv":
        logger.info("Default export Path is used: export_iperf.csv")

    listOfFiles = getListOfFiles(args.path)

    logger.info("Export Path is: " + args.export)

    with open(args.export, mode='w') as csv_file:
        fieldnames = ['runtime', 'image_name', 'ressource_limit', 'repeat', 'duration', 'type', 'send', 'received', 'filepath']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writeheader()
        
        for file in listOfFiles:
            tb_file = TimeBenchResult(file)
            tb_file.readInformationFromFile()
            tb_file.readInformationFromPath(args.path)
            writer.writerow({'runtime': tb_file.runtime, 
                            'image_name': tb_file.image_name, 
                            'ressource_limit': tb_file.ressource_limit, 
                            'repeat': tb_file.repeat,
                            'duration': tb_file.duration,
                            'type': tb_file.type,
                            'send': tb_file.send,
                            'received': tb_file.received, 
                            'filepath': tb_file.filepath})

if __name__ == '__main__':
    main()