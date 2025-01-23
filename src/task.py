class Task:
    def __init__(self, arrival_time: int, burst_time: int, resources: list[int, int]):
        self.arrival_time = arrival_time
        self.remaining_time = burst_time
        self.resources = resources

class Sub1Task(Task):
    def __init__(self, arrival_time: int, burst_time: int, resources: list[int], first_cpu):
        super().__init__(arrival_time, burst_time, resources)
        self.first_cpu = first_cpu
    pass

class Sub2Task(Task):
    pass

class Sub3Task(Task):
    pass