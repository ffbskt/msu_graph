import time
from datetime import datetime
import os


#timestamp = dt.replace(tzinfo=timezone.utc).timestamp()

def write_log(file=os.path.dirname(__file__) + '/../log.txt', log='none'):
    with open(file, 'a') as dt:
        log = str(datetime.fromtimestamp(time.time())) + ' /' + log + '\n'
        dt.write(log)
        dt.close()



if __name__ == "__main__":
    write_log(log='l')