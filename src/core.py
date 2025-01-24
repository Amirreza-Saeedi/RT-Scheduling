from task import Task

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
        return f'{self.name}: {self.running_task.name if self._is_idle == False else "Idle"}'
    
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
            # # Perform work in this quantum
            # with self.quantum_lock:
            #     print(f"Subsystem {subsystem_id} - CPU {cpu_id} working in Quantum {self.current_quantum}")
            
            # # Simulate logical work
            # self.do_sub_work(subsystem_id, cpu_id)
            
            # # Indicate work is complete
            # with self.quantum_lock:
            #     print(f"Subsystem {subsystem_id} - CPU {cpu_id} finished work in Quantum {self.current_quantum}")
            
            # Wait for the quantum to end
            self.barrier.wait()
            
            pass

    def do_task(self):
        self.running_task.burst_time -= 1
        self.active_time += 1
        self.timer += 1
        
        if self.timer == self.running_task.weight:
            self.timer = 0
            self._is_idle = True

    def is_idle(self):
        return self._is_idle

        
