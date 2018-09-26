class FakeFile:
    def __init__(self, size, content, progress_int = 30):
        self._total_size = size
        self._size = 0
        self._content = content
        self._uploaded = 0
        self._uploaded_since = 0
        self._ts = None
        self._started = None

    def _readbytes(self, num):
        self._size += num
        return bytes((num * self._content).encode('utf-8'))

    def read(self, num = -1):
        if self._started is None:
            self._started = datetime.now()
        if num == -1:
            return self._readbytes(self._total_size)
        if self._total_size == self._size:
            return bytes()
        elif self._total_size < self._size + num:
            return self._readbytes(self._total_size - self._sizes)
        return self._readbytes(num * self._content)

    def close(self):
        return True
