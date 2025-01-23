from abc import ABC, abstractmethod
from threading import Semaphore, Thread, Barrier, Lock


current_quantum = 0
quantum_lock = Lock()
barrier = Barrier(10)  # main + sub1 + 3cpu + sub2 + 2cpu + sub3 + 1cpu
quantum_limit = 50

class MainSystem:

    def __init__(self, args1: dict, args2: dict, args3: dict):
        '''
            :param args1: {resources:list[r1, r2], tasks:list}
        '''
        self.sub1 = SubSystem1(args1)
        self.sub2 = SubSystem1(args2)
        self.sub3 = SubSystem1(args3)

    def main(self):
        sub1_thread = Thread(target=self.sub1.run)
        sub1_thread.start()
        sub1_thread.is_alive()
        
        # main loop
        while current_quantum < quantum_limit:
            
            with quantum_lock:
                print(f"Quantum {current_quantum} starting.")
            
            # Signal all threads to start their work for the quantum
            barrier.wait()

            # print subs logs
            self.print_logs()
            
            # Wait for all threads to finish the quantum
            barrier.wait()
            
            with quantum_lock:
                print(f"Quantum {current_quantum} finished.\n")
                current_quantum += 1

    def print_logs(self):
        pass

    def get_sub1_log(self):
        pass

    def get_sub2_log(self):
        pass
        
    def get_sub3_log(self):
        pass

class _SubSystem(ABC):

    def __init__(self, args:dict):
        self.resources = args['resources'] 
        self.r1_sem = Semaphore(self.resources[0])
        self.r2_sem = Semaphore(self.resources[1])
        self.tasks = args['tasks']

    @abstractmethod
    def select_next():
        ''' Scheduling algorithm '''
        NotImplemented

    @abstractmethod
    def run():
        ''' Creates CPU threads '''
        NotImplemented
 
class SubSystem1(_SubSystem):
    # Start threads for subsystems
    threads = []
    core_count = 3
    waiting_queue = []

    def __init__(self,args:dict):
        super().__init__(args)

    def select_next():
        ''' WRR '''

    def run(self):
        for cpu_id in range(1, self.core_count+1):
            self.threads.append(Thread(target=subsystem_task, args=(self.select_next)))

        # main loop
        while current_quantum < quantum_limit:

            # update waiting
            ''' 
                waiting -> ready_x (load balancing)
            '''

            # 

            # while True:
            # # Wait for the quantum to start
            # self.barrier.wait()
            
            # # Perform work in this quantum
            # with self.quantum_lock:
            #     print(f"Subsystem {subsystem_id} - CPU {cpu_id} working in Quantum {self.current_quantum}")
            
            # # Simulate logical work
            # self.do_sub_work(subsystem_id, cpu_id)
            
            # # Indicate work is complete
            # with self.quantum_lock:
            #     print(f"Subsystem {subsystem_id} - CPU {cpu_id} finished work in Quantum {self.current_quantum}")
            
            # # Wait for the quantum to end
            # self.barrier.wait()
    
class SubSystem2(_SubSystem):
    ready_queue = []

    def select_next():
        ''' SRTF '''

class SubSystem3(_SubSystem):


    def select_next():
        ''' Rate Monotonic '''    
