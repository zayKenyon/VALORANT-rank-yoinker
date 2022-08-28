"""Log VALORANT chat messages"""
# pylint: disable=redefined-builtin
from re import compile
from glob import glob
from locale import getpreferredencoding
from os import mkdir, getcwd


class ChatLogging:
    """Handles logging the VALORANT chat to the chat_log folder"""

    def __init__(self):
        self.chat_file_opened = False

    def chat_log(self, string_to_log: str):
        """Creates a folder for and logs for chat."""
        try:
            mkdir(getcwd() + r"\chat_logs")
        except FileExistsError:
            pass
        filenames = []
        for filename in glob(r"chat_logs/chat_log-*.txt"):
            filenames.append(int(filename[19:-4]))
        if len(filenames) == 0:
            filenames.append(0)
        if self.chat_file_opened:
            with open(f"chat_logs/chat_log-{max(filenames)}.txt",
                      "a", encoding=getpreferredencoding()) as log_file:
                log_file.write(
                    f"""{self.to_plain(string_to_log.encode('ascii',
'replace').decode())}\n""")
        else:
            with open(f"chat_logs/chat_log-{max(filenames) + 1}.txt",
                      "w", encoding=getpreferredencoding()) as log_file:
                self.chat_file_opened = True
                log_file.write(
                    f"""{self.to_plain(string_to_log.encode('ascii',
'replace').decode())}\n""")

    @staticmethod
    def to_plain(line):
        """Converts coloured ANSI into plaintext."""
        ansi_escape = compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)
