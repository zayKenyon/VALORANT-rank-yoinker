# This code imports the `glob`, `os`, and `time` modules
import glob
import os
import time

# The `Logging` class is defined
class Logging:
    # The class constructor initializes the `logFileOpened` attribute as `False`
    def __init__(self):
        self.logFileOpened = False

    # The `log` method takes a string `log_string` as an argument
    def log(self, log_string: str):
        # The logs directory is determined
        logs_directory = os.getcwd() + "/logs"

        # If the logs directory does not exist, it is created
        if not os.path.exists(logs_directory):
            os.mkdir(logs_directory)
        
        # A list of log files is obtained using the `glob` module
        log_files = glob.glob(r"logs/log-*.txt")

        # The log file numbers are extracted from the filenames
        log_file_numbers = [int(file[9:-4]) for file in log_files]
        
        # If no log files exist, a log-0.txt file is created
        if not log_file_numbers:
            log_file_numbers.append(0)
        
        # The log file name is determined
        log_file_name = f"logs/log-{max(log_file_numbers) + 1 if not self.logFileOpened else max(log_file_numbers)}.txt"

        # The log file is opened and written to
        with open(log_file_name, "a" if self.logFileOpened else "w") as log_file:
            self.logFileOpened = True

            # The current time is formatted
            current_time = time.strftime("%Y.%m.%d-%H.%M.%S", time.localtime(time.time()))

            # The log string is written to the file with the current time as a prefix
            log_file.write(f"[{current_time}] {log_string.encode('ascii', 'replace').decode()}\n")