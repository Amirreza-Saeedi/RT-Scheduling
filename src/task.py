from enum import Enum

class Task:
    
    
    class State(Enum):
        WAITAING    = 1
        READY       = 2
        RUNNING     = 3
        
    def __init__(self, name: str, arrival_time: int, burst_time: int, resources: list[int, int]):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.resources = resources
        self.state = self.State.WAITAING

    def __str__(self) -> str:
        return self.name
    
    def is_finished(self):
        return self.burst_time == 0

class Sub1Task(Task):
    weight = 0
    def __init__(self, name: str, arrival_time: int, burst_time: int, resources: list[int], first_cpu: int):
        super().__init__(name, arrival_time, burst_time, resources)
        self.first_cpu = first_cpu
    pass

class Sub2Task(Task):
    def __init__(self, name: str, arrival_time: int, burst_time: int, resources: list[int]):
        super().__init__(name, arrival_time, burst_time, resources)
    pass

class Sub3Task(Task):
    def __init__(self, name: str, arrival_time: int, burst_time: int, resources: list[int], period: int,cycle_count: int):
        super().__init__(name, arrival_time, burst_time, resources)
    pass