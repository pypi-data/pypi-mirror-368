# Added by Mahesh Saggam on [29-JUNE-21] To print console in a separate log file

import logging
from logging.handlers import RotatingFileHandler
# from jproperties import Properties
import os
import traceback
from datetime import datetime
import random

dir = 'transaction_log'

if not os.path.exists(dir):
    os.makedirs(dir)

for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

# The below commented code will required if the configuration is defined in Properties file

# configs = Properties()
# propDetails = {}

# with open('PythonLogger.Properties', 'rb') as read_prop:
#     configs.load(read_prop)


# prop_view = configs.items()

# for item in prop_view:
#     propDetails[item[0]] = item[1].data

# format = propDetails['FORMAT']
# filename = propDetails['FILE_NAME']
# filemode = propDetails['FILE_MODE']
# loggerName = propDetails['LOGGER_NAME']
# maxBytes = propDetails['MAX_BYTES']
# backUpcount = propDetails['BACKUP_COUNT']

format = '%(asctime)s %(levelname)s %(name)s %(message)s'
random_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'{random_number}_{timestamp}.log'
filemode = 'w'
loggerName = '[TransLogger]'
maxBytes = 5242880
backUpcount = 100
ibaseDebugLvl = 10

logging.basicConfig(format=format,
                    filename=dir + '/' + filename,
                    filemode=filemode,
                    level=logging.DEBUG)
deployment_logger = logging.getLogger(loggerName)
deployment_logger.propagate = False
logHandler = RotatingFileHandler(dir + '/' + filename, maxBytes=int(maxBytes), backupCount=int(backUpcount))
formatter = logging.Formatter(format)
logHandler.setFormatter(formatter)
deployment_logger.addHandler(logHandler)

def deployment_log(msg, debugLevel='0'):
    stack = traceback.extract_stack()
    filename, line, functionName, text = stack[-2]
    index = filename.rfind('/')
    filename = filename[index + 1:]
    msg = '~' + filename + '~' + functionName + '~' + msg

    if debugLevel.strip() == '':
        debugLevel = 0
    else:
        debugLevel = int(debugLevel)

    # to print normal log use debugLvl 1
    if debugLevel == 0:
        deployment_logger.debug(msg)

    # to print stack trace use debugLvl 9
    if debugLevel == 1:
        deployment_logger.exception(msg)
