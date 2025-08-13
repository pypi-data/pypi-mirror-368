# -*- coding: utf-8 -*-.
import os
import json
import pandas as pd

class JsonOperation:
    @staticmethod
    def read_config_content():
        current_directory = os.path.dirname(__file__) + "/resources/config"
        with open(current_directory, 'r') as file:
            result = json.load(file)
        return result
    
    @staticmethod
    def read_start_point():
        current_directory = os.path.dirname(__file__) + "/resources/start_point_config"
        with open(current_directory, 'r') as file:
            result = json.load(file)
        return result
