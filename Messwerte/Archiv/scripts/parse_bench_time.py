
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
        self.real_time = -1.0
        self.user_time = -1.0
        self.sys_time = -1.0
        self.ressource_limit = ""
        self.runtime = ""
        self.image_name = ""
        self.repeat = ""
        
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
            self.real_time = re.findall(r"real\s*0m(\d+.?\d+)", filetext)[0]
            self.user_time = re.findall(r"user\s*0m(\d+.?\d+)", filetext)[0]
            self.sys_time = re.findall(r"sys\s*0m(\d+.?\d+)", filetext)[0]
        except Exception:
            logger.error("Parsing error in: " + self.filepath,  exc_info=True) 

    def readInformationFromPath(self, basePath):

        workingPath = self.filepath.replace(basePath, '')
        pathParts = workingPath.split('/')

        try: 
            if len(pathParts) == 5:
                self.ressource_limit = pathParts[0]
                self.runtime = pathParts[1]
                self.image_name = pathParts[2]
                self.repeat = pathParts[3].replace('repeat_', '')
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

    parser.add_argument("--path", default="C:\\Work\\Bachelorarbeit\\Auswertung\\Raw\\apache_benchmark\\", help="Input Path")
    parser.add_argument("--export", default="export.csv", help="Export Path")

    args = parser.parse_args()

    if args.export == "export.csv":
        logger.info("Default export Path is used: export.csv")

    listOfFiles = getListOfFiles(args.path)

    logger.info("Export Path is: " + args.export)

    with open(args.export, mode='w') as csv_file:
        fieldnames = ['runtime', 'image_name', 'ressource_limit', 'repeat', 'real_time', 'user_time', 'sys_time', 'filepath']
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
                            'real_time': tb_file.real_time,
                            'user_time': tb_file.user_time, 
                            'sys_time': tb_file.sys_time,
                            'filepath': tb_file.filepath})

if __name__ == '__main__':
    main()