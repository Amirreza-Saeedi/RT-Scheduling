from abc import ABC, abstractmethod
from threading import Semaphore, Thread, Barrier, Lock
from core import *
from task import *
import math
import numpy as np

current_quantum = 0
quantum_lock = Lock()
barrier = Barrier(10)  # main + sub1 + 3cpu + sub2 + 2cpu + sub3 + 1cpu
quantum_limit = 20
log_barrier = Barrier(4)  # main + 3 subs
resources_barrier = Barrier(3)  # sub1 + sub2 + sub3 

class MainSystem:

    def __init__(self, args1: dict, args2: dict, args3: dict):
        '''
            :param args1: {resources:list[r1, r2], tasks:list}
        '''
        self.sub1 = SubSystem1(args1)
        self.sub2 = SubSystem2(args2)
        self.sub3 = SubSystem3(args3, args1['resources'], args2['resources'])

    def main(self):
        sub1_thread = Thread(target=self.sub1.run)
        sub1_thread.start()
        sub2_thread = Thread(target=self.sub2.run)
        sub2_thread.start()
        sub3_thread = Thread(target=self.sub3.run)
        sub3_thread.start()
    
        global current_quantum
        
        # main loop
        while current_quantum < quantum_limit:
            
            barrier.wait()
                        
            log_barrier.wait()  # sig in
            self.print_logs()
            log_barrier.wait()  # sig out
            
            # Wait for all threads to finish the quantum
            barrier.wait()
            
            with quantum_lock:
                # print subs logs
                current_quantum += 1

    def print_logs(self):
        print(f'~ quantum {current_quantum}:')
        print(self.get_sub1_log())
        print(self.get_sub2_log())
        print(self.get_sub3_log())

    def get_sub1_log(self):
        s = 'sub1:\n'
        s += f'\tfree resources: {self.sub1.resources}\n'
        s += f'\twaiting queue: {[(t.name, t.burst_time) for t in self.sub1.waiting_queue]}\n'
        for i in range(self.sub1.core_count):
            s += f'\t{self.sub1.cores[i].name}:\n'
            s += f'\t\trunning task: {self.sub1.cores[i]}\n'
            s += f'\t\tready queue: {[(t.name, t.burst_time) for t in self.sub1.ready_queues[i]]}\n'
        return s

    def get_sub2_log(self):
        s = 'sub2:\n'
        s += f'\tfree resources: {self.sub2.resources}\n'
        s += f'\tready queue: {[(t.name, t.burst_time) for t in self.sub2.ready_queue]}\n'
        for i in range(self.sub2.core_count):
            s += f'\t{self.sub2.cores[i].name}:\n'
            s += f'\t\trunning task: {self.sub2.cores[i]}\n'
        return s
        
    def get_sub3_log(self):
        s = 'sub3:\n'
        s += f'\twaiting queue: {[(t.name, t.cycle_count, t.remaining_time) for t in self.sub3.waiting_queue]}\n'
        s += f'\tfree resources: {self.sub3.resources}\n'
        s += f'\tready queue: {[(t.name, t.cycle_count, t.remaining_time) for t in self.sub3.ready_queue]}\n'
        s += f'\t{self.sub3.core.name}:\n'
        s += f'\t\trunning task: {self.sub3.core}\n'
        return s

class _SubSystem(ABC):
    cpu_lock = Lock()

    def __init__(self, args:dict):
        self.resources = args['resources'] 
        self.tasks: list[Task] = args['tasks']

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

    def do_load_balance(self):

        all_tasks = []
        for i, q in enumerate(self.ready_queues):
            for t in q:
                if t.is_started():
                    all_tasks.append(t)
                    self.ready_queues[i].remove(t)

        for t in all_tasks:
            idx = min([0, 1, 2], key=lambda x: len(self.ready_queues[x]) + 1 if not self.cores[x].is_idle() else 0)
            self.ready_queues[idx].append(t)
        

    def run(self):
        for cpu_id in range(self.core_count):
            self.threads.append(Thread(target=self.cores[cpu_id].run))
            self.threads[cpu_id].start()
   
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
                resources_barrier.wait()

                ### tasks to wait
                for i in range(len(self.tasks)):
                    if self.tasks[i].arrival_time == current_quantum:
                        self.waiting_queue.append(self.tasks[i])

                ### wait to ready
                to_remove = []
                for w in self.waiting_queue:
                    if self.resources[0] >= w.resources[0] and self.resources[1] >= w.resources[1]:
                        # assign
                        for j in range(2):  
                            self.resources[j] -= w.resources[j]
                        to_remove.append(w)
                        w.state = Task.State.READY
                        self.ready_queues[w.first_cpu - 1].append(w)
                for i in to_remove:
                    self.waiting_queue.remove(i)
                    
                self.do_load_balance()

                ### select from ready
                for i in range(self.core_count):
                    if self.cores[i].is_idle():
                        
                        # release finished task TODO
                        if self.cores[i].running_task != None and self.cores[i].running_task.is_finished():
                            for j in range(2):
                                self.resources[j] += self.cores[i].running_task.resources[j]
                            self.cores[i].running_task = None
                            
                        # running to ready queue
                        elif self.cores[i].running_task != None and not self.cores[i].running_task.is_finished():
                            self.cores[i].running_task.state = Task.State.READY
                            self.ready_queues[i].append(self.cores[i].running_task)

                        # ready queue to running
                        if len(self.ready_queues[i]) > 0:
                            selected_task = self.select_next(self.ready_queues[i])
                            self.cores[i].set_task(selected_task)
                        
                ### TODO load balance

                log_barrier.wait()
                log_barrier.wait()  
                
            barrier.wait()

class SubSystem2(_SubSystem):
    ready_queue: list[Sub2Task] = []
    threads: list[Thread] = []
    core_count = 2
    cores: list[Core2] = []
    tasks: list[Sub2Task] = []
    cpu_lock = Lock()

    def __init__(self,args:dict):
        super().__init__(args)
        for i in range(self.core_count):
            self.cores.append(Core2(f'core{i + 1}', barrier, self.cpu_lock))

    def sort(self):
        '''
        sort ready queue ascending by burst time
        '''
        self.ready_queue.sort(key=lambda task: task.burst_time)
    
    def select_next(self):
        ''' SRTF '''
        for t in self.ready_queue:
            if t.resources[0] <= self.resources[0] and t.resources[1] <= self.resources[1]:
                # self.ready_queue.remove(t)
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
                resources_barrier.wait()
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
                    if self.cores[i].running_task != None and self.cores[i].running_task.is_finished() :
                        self.cores[i].running_task.burst_time = -1  # flag; so only release resources once
                        for j in range(2):
                            self.resources[j] += self.cores[i].running_task.resources[j]

                    self.sort()

                    # no running task
                    if self.cores[i].running_task == None or \
                        self.cores[i].running_task.is_finished() or self.cores[i].running_task.burst_time == -1 :
                        # if len(self.ready_queue) > 0:
                        task = self.select_next()
                        if task != None:
                            self.ready_queue.remove(task)
                            for j in range(2):  # assign resources
                                self.resources[j] -= task.resources[j]
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
                        if task == None or task.burst_time >= self.cores[i].running_task.burst_time:
                            for j in range(2):
                                self.resources[j] -= self.cores[i].running_task.resources[j]
                        # if not None 
                        else:
                            self.ready_queue.remove(task)
                            self.ready_queue.append(self.cores[i].running_task)
                            self.cores[i].running_task.state = Task.State.READY
                            self.cores[i].set_task(task)
                            task.state = Task.State.RUNNING

                            for j in range(2):
                                self.resources[j] -= task.resources[j]

                # log barrier
                log_barrier.wait()
                ''' printing logs '''
                log_barrier.wait()  

            barrier.wait()


class SubSystem3(_SubSystem):

    ready_queue: list[Sub3Task] = []
    waiting_queue: list[Sub3Task] = []
    thread: Thread
    core: Core3
    sub1_resources: list[int, int]
    sub2_resources: list[int, int]
    cpu_lock = Lock()


    def __init__(self, args: dict, sub1_resources: list, sub2_resources: list):
        super().__init__(args)
        self.sub1_resources = sub1_resources
        self.sub2_resources = sub2_resources
        self.core = Core3('core1', barrier, self.cpu_lock)

    def sort(self, l):
        ''' sort ascending by period time '''
        l.sort(key=lambda x: x.period)

    def cal_worst_case(self, new_task: Sub3Task):
        ''' N(2 ^ 1/N - 1) '''
        n = 1
        n += len(self.ready_queue) + 1 if not self.core.is_idle() else 0
        return n * (2 ** (1 / n) - 1)

    def cal_utilization(self, new_task: Sub3Task):
        u =  new_task.burst_time / new_task.period
        for task in self.ready_queue:
            u += task.burst_time / task.period
        u += 0 if self.core.is_idle() else (self.core.running_task.burst_time / self.core.running_task.period)
        return u
    
    def add_to_ready(self, waiting_task: Sub3Task):
        '''
        append to ready queue if possible,
        else release resources held temporarily by the task
        '''

        if self.cal_worst_case(waiting_task) > self.cal_utilization(waiting_task):
            waiting_task.state = Task.State.READY
            self.ready_queue.append(waiting_task)
            self.waiting_queue.remove(waiting_task)
            return True
        # release all
        waiting_task.release_all([self.sub1_resources, self.sub2_resources, self.resources])
        return False

    def select_next(self):
        ''' **Rate Monotonic**\n
        ready queue must be sorted before
        '''
        for t in self.ready_queue:
            if t.arrival_time <= current_quantum:
                return t
        return None

    def run(self):
        self.thread = Thread(target=self.core.run)
        self.thread.start()
        
        # main loop
        while True:

            with self.cpu_lock:
                barrier.wait()
                '''
                tasks to waiting
                ready to running (priority)
                running to ready (preemtp)

                '''
                ### tasks to waiting
                to_delete = []
                for t in self.tasks:
                    if t.arrival_time == current_quantum:
                        self.waiting_queue.append(t)
                        to_delete.append(t)
                        t.state = Task.State.WAITAING
                for t in to_delete:
                    self.tasks.remove(t)

                ### waiting to ready
                for w in self.waiting_queue:
                    ## try sub3 resources
                    w.assign(3, self.resources)  # assign temporarily
                    if w.is_fully_assigned():
                        self.add_to_ready(w)

                    else:
                        ## try sub1 & sub2 resources
                        w.assign(1, self.sub1_resources)  # sub1
                        if w.is_fully_assigned():
                            self.add_to_ready(w)
                        else:
                            w.assign(2, self.sub2_resources)  # sub2
                            if w.is_fully_assigned():
                                self.add_to_ready(w)
                            ## release all & keep w waiting
                            else:
                                w.release_all([self.sub1_resources, self.sub2_resources, self.resources])

                ### handle running & ready
                self.sort(self.ready_queue)
                ## running finished

                # ready to running
                '''
                first cpu task
                
                burst finished
                    arrive <= quantum
                
                preemption

                '''
                task = self.select_next()
                # first assignment
                if not self.core.running_task and task:  
                    self.ready_queue.remove([t for t in self.ready_queue if t.name == task.name][0])
                    task.state = Task.State.RUNNING
                    self.core.set_task(task)
                # burst finished
                elif self.core.running_task and self.core.is_idle():
                    old_task = self.core.running_task
                    if old_task.cycle_count != 0:  # back to ready
                        old_task.state = Task.State.READY
                        ready_set = set(self.ready_queue)
                        ready_set.add(old_task)
                        self.ready_queue = list(ready_set)
                    else:  # release
                        old_task.release_all([self.sub1_resources, self.sub2_resources, self.resources])  # XXX
                        self.core.running_task = None
                    if task:
                        self.ready_queue.remove([t for t in self.ready_queue if t.name == task.name][0])
                        task.state = Task.State.RUNNING
                        self.core.set_task(task)
                # preemption
                elif self.core.running_task and task and not self.core.is_idle() and \
                    task.period < self.core.running_task.period:
                    old_task = self.core.running_task
                    old_task.state = Task.State.READY
                    ready_set = set(self.ready_queue)
                    ready_set.add(old_task)
                    self.ready_queue = list(ready_set)
                    self.ready_queue.remove([t for t in self.ready_queue if t.name == task.name][0])
                    task.state = Task.State.RUNNING
                    self.core.set_task(task)


                # open resources for sub1 & sub2 XXX
                resources_barrier.wait() 
                # log barrier
                log_barrier.wait()
                ''' printing logs '''
                log_barrier.wait()  

            barrier.wait()


