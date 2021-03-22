#encoding: UTF-8
import shutil
from   logging.handlers import RotatingFileHandler
import os
import bz2
import logging.config
from multiprocessing import RLock
import time

# class my New Rotating File Handler
class NewRotatingFileHandler(RotatingFileHandler):

     def __init__(self, filename, mode, maxBytes, backupCount):

         super(NewRotatingFileHandler, self).__init__(filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount)
         self.backup_count = backupCount
         self.max_bytes    = maxBytes
         self.__zip_count  = 1
         self.__lock       = RLock()


     def emit(self, record):
         with self.__lock:
             """
                     Emit a record.

                     Output the record to the file, catering for rollover as described
                     in doRollover().
                     """
             try:
                 if self.shouldRollover(record):
                     self.doRollover()
                 logging.FileHandler.emit(self, record)
             except (KeyboardInterrupt, SystemExit):
                 raise
             except:
                 self.handleError(record)


     def doRollover(self):
         with self.__lock:
             try:
                 """
                 Do a rollover, as described in __init__().
                 """
                 new_source = self.baseFilename+"_"+str(self.__zip_count)+".log"
                 new_dest   = self.baseFilename+"_backup_"+str(self.__zip_count)+".zip"

                 if os.path.exists(new_source):
                     os.remove(new_source)

                 shutil.copy(self.baseFilename, new_source)
                 open(self.baseFilename, "w").close()

                 # read in old source and write in new destination
                 with open(new_source, "rb") as sf:
                    data = sf.read()
                    compressed = bz2.compress(data)
                    with open(new_dest, "wb") as df:
                        df.write(compressed)

                 self.__zip_count += 1
                 # check if count zip is greater than backup count, because if yes count zip will be reset to 1
                 if self.__zip_count > self.backupCount:
                     self.__zip_count = 1

                 df.close()  # close stream source
                 sf.close()  # close stream destination
                 time.sleep(2)
                 os.remove(new_source)  # remove source

             except Exception as ex:
                 print("Error dorollover: "+str(ex))