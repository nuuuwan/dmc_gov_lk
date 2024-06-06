import os


class RunMode:
    @staticmethod
    def is_test():
        return os.name == 'nt'
