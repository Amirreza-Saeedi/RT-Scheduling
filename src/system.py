from abc import ABC, abstractmethod
from threading import Semaphore, Thread, Barrier, Lock
from core import *
from task import *
import math


current_quantum = 0
quantum_lock = Lock()
barrier = Barrier(5)  # main + sub1 + 3cpu + sub2 + 2cpu + sub3 + 1cpu
quantum_limit = 20
log1_barrier = Barrier(2)
log2_barrier = Barrier(2)

class MainSystem:

    def __init__(self, args1: dict, args2: dict, args3: dict):
        '''
            :param args1: {resources:list[r1, r2], tasks:list}
        '''
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

            
            # sig in
            log1_barrier.wait()
            self.print_logs()
            # sig out
            log1_barrier.wait()

            
            # Wait for all threads to finish the quantum
            barrier.wait()
            
            with quantum_lock:
                # print subs logs
                # print(f"Quantum {current_quantum} finished.\n")
                current_quantum += 1

    def print_logs(self):

        print(f'~ quantum {current_quantum}:')
        log = self.get_sub1_log()
        print(log)
        pass

    def get_sub1_log(self):
        s = 'sub1:\n'
        s += f'\tfree resources: {self.sub1.resources}\n'
        s += f'\twaiting: {[t.name for t in self.sub1.waiting_queue]}\n'
        for i in range(self.sub1.core_count):
            s += f'\t{self.sub1.cores[i].name}:\n'
            s += f'\t\trunning task: {self.sub1.cores[i]}\n'
            s += f'\t\tready queue: {[t.name for t in self.sub1.ready_queues[i]]}\n'
        return s

    def get_sub2_log(self):
        pass
        
    def get_sub3_log(self):
        pass

class _SubSystem(ABC):
    cpu_lock = Lock()

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
        # self.waiting_queue = self.tasks

    def select_next(self, ready_queue: list[Task]):
        ''' WRR '''
        next_task = ready_queue[0]
        next_task.state = Task.State.RUNNING
        sum_burst = [t.burst_time for t in ready_queue]
        next_task.weight = math.ceil(next_task.burst_time / math.gcd(*sum_burst))
        ready_queue.pop(0)
        return next_task

    def run(self):
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


                    ### tasks to wait
                    for i in range(self.tasks):
                        if self.tasks[i].arrival_time == current_quantum:
                            self.waiting_queue.append(self.tasks[i])

                    ### wait to ready
                    # for each t if arrive
                    # ready = min(core)
                    # ready.append(t)
                    to_remove = []
                    for w in self.waiting_queue:
                        print('qqq', current_quantum)
                        print("Waiting_queue1111: ",[t.name for t in self.waiting_queue])
                        print(w.name, w.resources, w.arrival_time)
                        if self.resources[0] >= w.resources[0] and self.resources[1] >= w.resources[1]:
                            # assign
                            for j in range(2):  
                                self.resources[j] -= w.resources[j]
                            to_remove.append(w)
                            print("Waiting_queue----: ",[t.name for t in self.waiting_queue])
                            w.state = Task.State.READY
                            self.ready_queues[w.first_cpu - 1].append(w)
                        print("Waiting_queue2222: ",[t.name for t in self.waiting_queue])
                    
                    for i in to_remove:
                        self.waiting_queue.remove(i)
                        
                    ### select from ready
                    for i in range(self.core_count):
                        if self.cores[i].is_idle():
                            # print(f'>>>idle CPU{i}')
                            # print(f'rq{i}: {len(self.ready_queues[i])}')
                            
                            # release finished task
                            if self.cores[i].running_task != None and self.cores[i].running_task.is_finished():
                                
                                for j in range(2):
                                    self.resources[j] += self.cores[i].running_task.resources[j]
                                
                            # running to ready queue
                            elif self.cores[i].running_task != None and not self.cores[i].running_task.is_finished():
                                self.cores[i].running_task.state = Task.State.READY
                                self.ready_queues[i].append(self.cores[i].running_task)

                            # ready queue to running
                            if len(self.ready_queues[i]) > 0:
                                selected_task = self.select_next(self.ready_queues[i])
                                self.cores[i].set_task(selected_task)
                            
                    
                    ### load balance

                    log1_barrier.wait()
                    log1_barrier.wait()


                    # load balancing
                    
                barrier.wait()
    
class SubSystem2(_SubSystem):
    ready_queue: list[Sub2Task] = []
    threads: list[Thread] = []
    core_count = 2
    cores: list[Core2] = []
    tasks: list[Sub2Task] = []

    def __init__(self,args:dict):
        super().__init__(args)
        for i in range(self.core_count):
            self.cores.append(Core2(f'core{i + 1}', barrier, self.cpu_lock))

    def sort(self):
        '''
        sort ready queue ascending by burst time
        '''
        self.ready_queue.sort(key=lambda a: a.burst_time)
    
    def select_next(self):
        ''' SRTF '''
        for t in self.ready_queue:
            if t.resources[0] <= self.resources[0] and t.resources[1] <= self.resources[1]:
                self.ready_queue.remove(t)
                # assign resources
                # t.state 
                return t
        return None

    def run(self):

        for cpu_id in range(self.core_count):
            self.threads.append(Thread(target=self.cores[cpu_id].run))
            self.threads[cpu_id].start()

        # main loop
        while True:

            with self.cpu_lock:
                barrier.wait()
                '''
                tasks to ready
                ready to running 
                running to ready (preemtp)
                '''
                
                ### tasks to ready
                for t in self.tasks:
                    if t.arrival_time == current_quantum:
                        self.ready_queue.append(t)

                ### 
                for i in range(self.core_count):

                    # release finished task
                    if self.cores[i].running_task != None and self.cores[i].running_task.is_finished():
                        for j in range(2):
                            self.resources[j] += self.cores[i].running_task.resources[j]

                    self.sort()

                    # no running task
                    if self.cores[i].running_task == None or self.cores[i].running_task.is_finished():
                        # if len(self.ready_queue) > 0:
                        task = self.select_next()
                        if task != None:
                            for j in range(2):  # assign resources
                                self.resources[j] += task.resources[j]
                            task.state = Task.State.RUNNING
                            self.cores[i].set_task(task)

                    # preemption
                    else: 
                        # release temporarily
                        for j in range(2):
                            self.resources[j] += self.cores[i].running_task.resources[j]
                        # select next
                        task = self.select_next()
                        # if None undo release
                        if task == None:
                            for j in range(2):
                                self.resources[j] -= self.cores[i].running_task.resources[j]
                        # if not None 
                        else:
                            self.ready_queue.append(self.cores[i].running_task)
                            self.cores[i].running_task.state = Task.State.READY
                            self.cores[i].set_task(task)
                            task.state = Task.State.RUNNING
                            for j in range(2):
                                self.resources[j] -= task.resources[j]

                # log barrier
                log2_barrier.wait()
                log2_barrier.wait()

                              
            



            barrier.wait()


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
