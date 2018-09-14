"""" by ffbskt
Load file from parent directory. Named GoogleDrivePermision.json and EmailPassLog
"""

import os.path
import json

GoogleDrivePermision = os.path.dirname(__file__) + '/GoogleDrivePermision.json'
file = open(os.path.dirname(__file__) + '/EmailPassLog')
EmailPassLog = json.loads(file.read())

if __name__ == "__main__":
    """ 
    You need two files ('EmailPassLog', 'GoogleDrivePermision.json'): 
    google drive permission to use google docs, 
    and file with line like down to use your mail (password of your mail and mail adress) 
    {"password": "*****", "log": "m______ra@gmail.com"} 
    
    This two files should be at upper directory (or another worlds in same with graph - project folder)
    """
    print(EmailPassLog, GoogleDrivePermision)