import sys
import resource


class recursionlimit:
    def __init__(self):
        self.old_limit = 1000

    def __enter__(self):
        resource.setrlimit(resource.RLIMIT_STACK, (0x10000000, resource.RLIM_INFINITY))
        sys.setrecursionlimit(0x100000)

    def __exit__(self, type, value, tb):
        sys.setrecursionlimit(self.old_limit)