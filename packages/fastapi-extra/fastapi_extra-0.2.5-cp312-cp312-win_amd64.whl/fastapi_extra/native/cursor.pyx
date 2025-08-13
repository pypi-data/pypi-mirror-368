cimport cython
from cpython cimport time

import datetime


cdef int _sequence_length = 10
cdef double _start_point = datetime.datetime(2020, 1, 1).timestamp()


@cython.no_gc
cdef class Cursor:
    __slots__ = "cursor", "last_point"
    cdef:
        int cursor
        int seed
        long long last_point

    def __init__(self, seed: int):
        self.seed = seed
        if self.seed > 16:
            self.seed %= 16
        self.cursor = 0
        self.last_point = 0

    cdef inline long long fetch(self) nogil:
        cdef:
            long long count = 0
            long long point = int((time.time() - _start_point) * 100)

        if self.last_point == point:
            count = self.cursor + 1
            if count >= (1 << _sequence_length):
                return 0
        else:
            self.last_point = point
        self.cursor = count
        return (point << (_sequence_length + 4)) + (self.seed << _sequence_length) + count

    def next_val(self) -> int:
        index = self.fetch()
        while index == 0:
            index = self.fetch()
        return index
