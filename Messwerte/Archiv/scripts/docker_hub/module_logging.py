#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import json
from logging.handlers import RotatingFileHandler
# Import StringIO from IO if Python3
try:
    from StringIO import StringIO as StringBuffer
except ImportError:
    from io import StringIO as StringBuffer


class Logger():
    def __init__(self):
        self.log_buffer = StringBuffer()  # create buffer for storing log entries

    def add_buffering_handler(self, target_logger, buffer):
        """
        Adds a buffering log handler to a logger.
        :param target_logger: The logger to add the buffering handler to
        :param buffer: The buffer (a StringIO instance)
        """
        buffering_handler = logging.StreamHandler(buffer)
        buffering_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        buffering_handler.setFormatter(formatter)

        target_logger.addHandler(buffering_handler)

    def add_file_handler(self, target_logger, log_file_path):
        """
        Adds a rotating file log handler to a logger
        :param target_logger: The logger to add the handler to
        :param log_file_path: The path of the log file (e.g. logs/log.txt)
        """
        file_handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=3)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        target_logger.addHandler(file_handler)

    def log_file_path(self, module_name):
        """
        Gets the path for the log file. When present ./logs is used as log storage location
        else the path /ansible/logs is used (and also created if not present)
        Note that log file rotation (max 5 log files with 10MB in size) is used here to prevent
        storage fill up.
        :param module_name: The name of the current module which will also be the filename
        :return the log file path
        """
        log_path = "logs"
        if not os.path.isdir(log_path):
            log_path = "/opt/ansible/logs"
            if not os.path.isdir(log_path):
                os.mkdir(log_path)

        return "{dir}/{module_name}.log".format(dir=log_path, module_name=module_name)

    def init_logging(self, log_to_json_result=False):
        """
        Initializes the logging system by configuring the root logger and creating a logger
        for the current module.
        :return: the logger for the current module
        """
        # configure root logger
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        root_logger.addHandler(consoleHandler)

        if log_to_json_result:
            self.add_buffering_handler(root_logger, self.log_buffer)

        return root_logger
