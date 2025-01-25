from task import *

class Core:

    # Core class attributes
    running_task: Task = None  # Currently running task
    active_time = 0  # Total time spent on tasks
    _is_idle = True  # Flag indicating if the core is idle
    timer = 0  # Timer for task execution   


    def __init__(self, name, barrier, lock):
        self.name = name
        self.barrier = barrier
        self.lock = lock
        
    def __str__(self) -> str:
        return f'{self.name}: {(self.running_task.name, self.running_task.burst_time) if self._is_idle == False else "Idle"}'
    
    def set_task(self, task: Task):
        self.running_task = task
        self._is_idle = False
    
    def run(self):
        while True:
            # Wait for the quantum to start
            self.barrier.wait()
            with self.lock:
                if not self.is_idle():
                    self.do_task()
                    
            # Wait for the quantum to end
            self.barrier.wait()
            

    def do_task(self):
        # print(f'{self.name}, {self.running_task.name}, burst({self.running_task.burst_time}), weight({self.running_task.weight})')
        self.running_task.burst_time -= 1
        self.active_time += 1
        self.timer += 1
        
        if self.timer == self.running_task.weight:
            self.timer = 0
            self._is_idle = True

    def is_idle(self):
        return self._is_idle

        
class Core2:
    # Core class attributes
    running_task: Task = None  # Currently running task
    active_time = 0  # Total time spent on tasks
    _is_idle = True  # Flag indicating if the core is idle


    def __init__(self, name, barrier, lock):
        self.name = name
        self.barrier = barrier
        self.lock = lock
        
    def __str__(self) -> str:
        return f'{self.name}: {(self.running_task.name, self.running_task.burst_time) if self._is_idle == False else "Idle"}'
    
    def set_task(self, task: Task):
        self.running_task = task
        self._is_idle = False
    
    def run(self):
        while True:
            # Wait for the quantum to start
            self.barrier.wait()
            with self.lock:
                if not self.is_idle():
                    self.do_task()
                    
            # Wait for the quantum to end
            self.barrier.wait()
            

    def do_task(self):
        # print(f'{self.name}, {self.running_task.name}, burst({self.running_task.burst_time})')
        self.running_task.burst_time -= 1
        self.active_time += 1
        
        if self.running_task.burst_time == 0:
            self._is_idle = True

    def is_idle(self):
        return self._is_idle

    
class Core3:
    # Core class attributes
    running_task: Sub3Task = None  # Currently running task
    active_time = 0  # Total time spent on tasks
    _is_idle = True  # Flag indicating if the core is idle


    def __init__(self, name, barrier, lock):
        self.name = name
        self.barrier = barrier
        self.lock = lock
        
    def __str__(self) -> str:
        return f'{self.name}: {(self.running_task.name, self.running_task.burst_time) if self._is_idle == False else "Idle"}'
    
    def set_task(self, task: Task):
        self.running_task = task
        self._is_idle = False
    
    def run(self):
        while True:
            # Wait for the quantum to start
            self.barrier.wait()
            with self.lock:
                if not self.is_idle():
                    self.do_task()
                    
            # Wait for the quantum to end
            self.barrier.wait()
            

    def do_task(self):
        # print(f'{self.name}, {self.running_task.name}, burst({self.running_task.burst_time})')
        self.running_task.remaining_time -= 1
        self.active_time += 1
    
        
        if self.running_task.remaining_time == 0:
            self.running_task.cycle_count -= 1
            self.running_task.arrival_time += self.running_task.period  # update
            self._is_idle = True

    def is_idle(self):
        return self._is_idle

    