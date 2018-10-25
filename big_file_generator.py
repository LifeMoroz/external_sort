import random
import string


class Generator:
    CHUNK_SIZE = 10000

    def __init__(self, file_size, max_line_len):
        if file_size < 0:
            raise ValueError('File size can not be negative value')
        if max_line_len < 0:
            raise ValueError('Line size can not be negative value')

        self.file_size = file_size
        self.max_line_len = max_line_len
        self._chunks = self.file_size // self.CHUNK_SIZE

    def line_generator(self, fd):
        raise NotImplementedError('You must implement this function in subclasses')

    def generate(self, filename: str) -> bool:
        try:
            with open(filename, 'w+') as fd:
                self.line_generator(fd)
        except OSError as e:
            print('Exception happened while trying to open the file')
            print('Original exception was:', str(e))  # logging.exception()
            return False
        return True

    def _get_random_row(self):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, self.max_line_len))) + '\n'


class ASCIIRandomGenerator(Generator):

    def line_generator(self, fd):
        if fd.closed or not fd.writable():
            raise ValueError('Wrong file descriptor')

        for _ in range(self._chunks):
            fd.writelines([self._get_random_row() for _ in range(self.CHUNK_SIZE)])

        fd.writelines([self._get_random_row() for _ in range(self.file_size - self._chunks * self.CHUNK_SIZE)])


class CachedRowsGenerator(Generator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rows_cache = None
        self._cache_size = min(self.CHUNK_SIZE, self.file_size)

    def _fill_cache(self, ):
        self._rows_cache = [self._get_random_row() for _ in range(self._cache_size)]

    def _get_row(self,):
        if not self._rows_cache:
            self._fill_cache()
        return self._rows_cache[random.randint(0, self._cache_size - 1)]

    def line_generator(self, fd):
        for _ in range(self.file_size // self.CHUNK_SIZE):
            fd.writelines([self._get_row() for _ in range(self.CHUNK_SIZE)])
