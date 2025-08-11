#! python

from time import time


class SpiLog():
    def __init__(self, filename: str):
        try:
            self._log = open(filename, 'w')
        except Exception:
            raise
        self._now = time()

    def __del__(self):
        self._log.close()

    def log(self, size, write, read):
        self._log.write(f'{time()-self._now}:{size}:{write}:{read}\n')

    def log_str(self, txt):
        self._log.write(f'{time()-self._now}:{txt}\n')
