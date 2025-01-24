from abc import ABC, abstractmethod
from threading import Semaphore, Thread, Barrier, Lock
from core import Core
from task import *
import math


current_quantum = 0
quantum_lock = Lock()
barrier = Barrier(5)  # main + sub1 + 3cpu + sub2 + 2cpu + sub3 + 1cpu
quantum_limit = 50

class MainSystem:

    def __init__(self, args1: dict, args2: dict, args3: dict):
        '''
            :param args1: {resources:list[r1, r2], tasks:list}
        '''
        print("\n\n")
        for key, value in args1.items():
            print(f"{key}: {value}")
        print("\n\n")
        self.sub1 = SubSystem1(args1)
        # self.sub2 = SubSystem1(args2)
        # self.sub3 = SubSystem1(args3)

    def main(self):
        sub1_thread = Thread(target=self.sub1.run)
        sub1_thread.start()
        global current_quantum
        
        # main loop
        while current_quantum < quantum_limit:
            
            # with quantum_lock:
            #     print(f"Quantum {current_quantum} starting.")
            
            # Signal all threads to start their work for the quantum
            barrier.wait()

            # print subs logs
            self.print_logs()
            
            # Wait for all threads to finish the quantum
            barrier.wait()
            
            with quantum_lock:
                # print(f"Quantum {current_quantum} finished.\n")
                current_quantum += 1

    def print_logs(self):
        print(f'quantum {current_quantum}:')
        log = self.get_sub1_log()
        print(log)
        pass

    def get_sub1_log(self):
        s = 'sub1:'
        s += f'\t{self.sub1.resources}'
        s += f'\t{self.sub1.waiting_queue}'
        for i in range(self.sub1.core_count):
            s += f'\t{self.sub1.cores[i].name}:'
            s += f'\trunning task: {self.sub1.cores[i]}'
            s += f'\tready queue: {self.sub1.ready_queues[i]}'
        return

    def get_sub2_log(self):
        pass
        
    def get_sub3_log(self):
        pass

class _SubSystem(ABC):

    def __init__(self, args:dict):
        self.resources = args['resources'] 
        # self.r1_sem = Semaphore(self.resources[0])
        # self.r2_sem = Semaphore(self.resources[1])
        self.tasks = args['tasks']

    @abstractmethod
    def select_next(ready_queue: list[Task]):
        ''' Scheduling algorithm '''
        NotImplemented

    @abstractmethod
    def run():
        ''' Creates CPU threads '''
        NotImplemented
 
class SubSystem1(_SubSystem):
    # Start threads for subsystems
    threads: list[Thread] = []
    core_count = 3
    waiting_queue: list[Sub1Task] = []
    tasks: list[Sub1Task]
    cpu_lock = Lock()
    ready_queues: list[list[Sub1Task]] = [[], [], []]
    cores: list[Core] = []

    def __init__(self, args:dict):
        super().__init__(args)
        for i in range(self.core_count):
            self.cores.append(Core(f'core{i + 1}', barrier, self.cpu_lock))
        self.waiting_queue = self.tasks

    def select_next(self, ready_queue: list[Task]):
        ''' WRR '''
        next_task = ready_queue.pop(0)
        print('@@@ ready q:', ready_queue)
        sum_burst = [t.burst_time for t in ready_queue]
        print('@@@ sum burst:', sum_burst)
        next_task.weight = math.ceil(next_task.burst_time / math.gcd(*sum_burst))
        return next_task

    def run(self):
        print("---waiting queue1: ",self.waiting_queue)
        for cpu_id in range(self.core_count):
            self.threads.append(Thread(target=self.cores[cpu_id].run))
            self.threads[cpu_id].start()


        # main loop
        while current_quantum < quantum_limit:
            # update waiting
            ''' 
                waiting -> ready_i (load balancing)
                ready_i -> ready_j
                weight = next task / gcd
                
            '''

            while True:
                # Wait for the quantum to start

                with self.cpu_lock:
                    barrier.wait()
                    ### wait to ready
                    # for each t if arrive
                    # ready = min(core)
                    # ready.append(t)
                    print("---waiting queue2: ",self.waiting_queue)
                    for w in self.waiting_queue:
                        print('self', self.resources[0])
                        print('w', w.resources[0])
                        if w.arrival_time <= current_quantum and \
                            self.resources[0] >= w.resources[0] and self.resources[1] >= w.resources[1]:
                            # assign
                            for j in range(2):  
                                self.resources[j] -= w.resources[j]
                            balance_index = min([0, 1, 2], key=lambda x: self.cores[x].active_time)  # for load balance sake
                            print('VVVV w:', w)
                            self.ready_queues[balance_index].append(w)

                    ### select from ready
                    for i in range(self.core_count):
                        if self.cores[i].is_idle():
                            # check release
                            if self.cores[i].running_task != None and self.cores[i].running_task.burst_time == 0:
                                # self.r1_sem.release(self.cores[i].running_task.resources[0])
                                # self.r2_sem.release(self.cores[i].running_task.resources[1])
                                for j in range(2):
                                    self.resources[j] += self.cores[i].running_task.resources[j]
                            elif self.cores[i].running_task != None:
                                self.ready_queues[i].append(self.cores[i].running_task)
                                print("^^^NoneTest: ", self.cores[i].running_task)
                            elif len(self.ready_queues[i]) > 0:
                                # select
                                for k in range(3):
                                    print(f'rq{k}: {self.ready_queues[k]}')
                                print('i start', i)
                                selected_task = self.select_next(self.ready_queues[i])
                                print('i end', i)
                                self.cores[i].set_task(selected_task)

                # # Perform work in this quantum
                # with self.quantum_lock:
                #     print(f"Subsystem {subsystem_id} - CPU {cpu_id} working in Quantum {self.current_quantum}")
                
                # # Simulate logical work
                # self.do_sub_work(subsystem_id, cpu_id)
                
                # # Indicate work is complete
                # with self.quantum_lock:
                #     print(f"Subsystem {subsystem_id} - CPU {cpu_id} finished work in Quantum {self.current_quantum}")
                
                # Wait for the quantum to end
                barrier.wait()
    
class SubSystem2(_SubSystem):
    ready_queue = []
    threads = []
    core_count = 2

    def __init__(self,args:dict):
        super().__init__(args)

    def run(self):
        for cpu_id in range(1, self.core_count+1):
            self.threads.append(Thread(target=subsystem_task, args=(self.select_next)))

        # main loop
        while current_quantum < quantum_limit:
            pass

    def select_next():
        ''' SRTF '''

class SubSystem3(_SubSystem):

    ready_queue = []
    waiting_queue = []
    threads = []
    core_count = 1

    def __init__(self,args:dict):
        super().__init__(args)

        def run(self):
            for cpu_id in range(1, self.core_count+1):
                self.threads.append(Thread(target=subsystem_task, args=(self.select_next)))

            # main loop
            while current_quantum < quantum_limit:
                pass

    def select_next():
        ''' Rate Monotonic '''    
