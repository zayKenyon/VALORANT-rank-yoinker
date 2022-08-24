import glob
import os
import time
import re

class ChatLogging:
    def __init__(self):
        self.chatFileOpened = False

    def chatLog(self, stringToLog: str):
        # creating logs folder
        try:
            os.mkdir(os.getcwd() + "\chat_logs")
        except FileExistsError:
            pass
        filenames = []
        for filename in glob.glob(r"chat_logs/chat_log-*.txt"):
            filenames.append(int(filename[19:-4]))
        if len(filenames) == 0:
            filenames.append(0)
        if self.chatFileOpened:
            with open(f"chat_logs/chat_log-{max(filenames)}.txt", "a") as logFile:
                logFile.write(f"{self.escape_ansi(stringToLog.encode('ascii', 'replace').decode())}\n")
        else:
            with open(f"chat_logs/chat_log-{max(filenames) + 1}.txt", "w") as logFile:
                self.chatFileOpened = True
                logFile.write(f"{self.escape_ansi(stringToLog.encode('ascii', 'replace').decode())}\n")

    def escape_ansi(self, line):
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)
