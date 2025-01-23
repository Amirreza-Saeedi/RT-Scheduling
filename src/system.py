from abc import ABC, abstractmethod
from threading import Semaphore, Thread


class MainSystem:

    def __init__(self, args1: list, args2: list, args3: list):

        pass

    def main():
        pass

class _SubSystem(ABC):

    def __init__(self, resources: list):
        self.resources = resources 
        self.r1_sem = Semaphore(resources[0])
        self.r2_sem = Semaphore(resources[1])

    @abstractmethod
    def select_next():
        ''' Scheduling algorithm '''
        NotImplemented
 
class SubSystem1(_SubSystem):
    def select_next():
        ''' WRR '''

class SubSystem2(_SubSystem):
    def select_next():
        ''' SRTF '''

class SubSystem3(_SubSystem):
    def select_next():
        ''' Rate Monotonic '''    
