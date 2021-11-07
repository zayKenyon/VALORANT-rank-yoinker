import glob
import os
import time

class Logging:
    def __init__(self):
        self.logFileOpened = False

    def log(self, stringToLog: str):
        # creating logs folder
        try:
            os.mkdir(os.getcwd() + "\logs")
        except FileExistsError:
            pass
        filenames = []
        for filename in glob.glob(r"logs/log-*.txt"):
            filenames.append(int(filename[9:-4]))
        if len(filenames) == 0:
            filenames.append(0)
        if self.logFileOpened:
            with open(f"logs/log-{max(filenames)}.txt", "a") as logFile:
                logFile.write(f"[{time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime(time.time()))}]"
                              f" {stringToLog.encode('ascii', 'replace').decode()}\n")
        else:
            with open(f"logs/log-{max(filenames) + 1}.txt", "w") as logFile:
                self.logFileOpened = True
                logFile.write(f"[{time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime(time.time()))}]"
                              f" {stringToLog.encode('ascii', 'replace').decode()}\n")
