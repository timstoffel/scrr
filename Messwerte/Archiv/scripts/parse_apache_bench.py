
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
class ApacheBenchResult:

    def __init__(self, path):
        self.filepath = path
        self.completed_requests = -1
        self.failed_requests = -1
        self.requests_per_second = -1.0
        self.request_duration = - 1.0
        self.ressource_limit = ""
        self.runtime = ""
        self.image_name = ""
        self.number_of_targets = ""
        self.repeat = ""
        self.targetId = ""
        
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
            self.completed_requests = re.findall(r"Complete requests:\s*(\d+)", filetext)[0]
            self.failed_requests = re.findall(r"Failed requests:\s*(\d+)", filetext)[0]
            self.requests_per_second = re.findall(r"Requests per second:\s*(\d+.?\d+)", filetext)[0]
            self.request_duration = re.findall(r"Time taken for tests:\s*(\d+.?\d+)", filetext)[0]
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
                self.number_of_targets = pathParts[3].replace('target_count_', '')
                self.repeat = pathParts[4].replace('repeat_', '')
                self.targetId = pathParts[5].replace('.txt', '')
            else:
                logger.error("Parsing error not six arguments in: " + self.filepath)
        except Exception:
            logger.error("Parsing Exception in: " + self.filepath,  exc_info=True)

class ApacheBenchRamResult:

    def __init__(self, path):
        self.filepath = path
        self.ram_usage = -1
        self.ressource_limit = ""
        self.runtime = ""
        self.image_name = ""
        self.number_of_targets = ""
        self.repeat = ""
        
    def __str__(self):
        return self.filepath

    def readInformationFromFile(self):

        try: 
            textfile = open(self.filepath, 'r')
            filetext = textfile.read()
            self.ram_usage = filetext.replace('\n', '')
            textfile.close()
        except Exception:
            logger.error("Opening of file failed: " + self.filepath,  exc_info=True) 

    def readInformationFromPath(self, basePath):

        workingPath = self.filepath.replace(basePath, '')

        pathParts = workingPath.split('/')

        try: 
            if len(pathParts) == 6:
                self.ressource_limit = pathParts[0]
                self.runtime = pathParts[1]
                self.image_name = pathParts[2]
                self.number_of_targets = pathParts[3].replace('target_count_', '')
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

    parser.add_argument("--path", default="C:\\Work\\Bachelorarbeit\\Auswertung\\Raw\\apache_benchmark\\", help="Input Path")
    parser.add_argument("--export", default="export.csv", help="Export Path")
    parser.add_argument("--exportram", default="export_ram.csv", help="Export RAM Path")

    args = parser.parse_args()

    if args.export == "export.csv":
        logger.info("Default export Path is used: export.csv")

    listOfFiles = getListOfFiles(args.path)

    logger.info("Export Path is: " + args.export)

    ramusageFiles = list()

    with open(args.export, mode='w') as csv_file:
        fieldnames = ['runtime', 'image_name', 'ressource_limit', 'number_of_targets', 'targetId', 'repeat', 'completed_requests', 'failed_requests', 'requests_per_second', 'request_duration', 'filepath']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writeheader()
        
        for file in listOfFiles:

            if Path(file).name == 'ram.txt':
                ramusageFiles.append(file)
            else:
                ab_file = ApacheBenchResult(file)
                ab_file.readInformationFromFile()
                ab_file.readInformationFromPath(args.path)
                writer.writerow({'runtime': ab_file.runtime, 
                                'image_name': ab_file.image_name, 
                                'ressource_limit': ab_file.ressource_limit, 
                                'number_of_targets': ab_file.number_of_targets,
                                'targetId': ab_file.targetId,
                                'repeat': ab_file.repeat, 
                                'completed_requests': ab_file.completed_requests,
                                'failed_requests': ab_file.failed_requests, 
                                'requests_per_second': ab_file.requests_per_second,
                                'request_duration': ab_file.request_duration,
                                'filepath': ab_file.filepath})
    
    with open(args.exportram, mode='w') as csv_file:
        fieldnames = ['runtime', 'image_name', 'ressource_limit', 'number_of_targets', 'repeat', 'ram_usage', 'filepath']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writeheader()
        
        for file in ramusageFiles:
            abr_file = ApacheBenchRamResult(file)
            abr_file.readInformationFromFile()
            abr_file.readInformationFromPath(args.path)
            writer.writerow({'runtime': abr_file.runtime, 
                            'image_name': abr_file.image_name, 
                            'ressource_limit': abr_file.ressource_limit, 
                            'number_of_targets': abr_file.number_of_targets,
                            'repeat': abr_file.repeat, 
                            'ram_usage': abr_file.ram_usage,
                            'filepath': abr_file.filepath})

if __name__ == '__main__':
    main()