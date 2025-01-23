import threading

class QuantumSystem:
    def __init__(self):
        self.current_quantum = 0
        self.quantum_limit = 10  # Number of quantums to simulate
        self.barrier = threading.Barrier(7)  # 1 main thread + 6 subsystem threads (3+2+1)
        self.quantum_lock = threading.Lock()  # Protect quantum counter
        
    def main_system(self):
        for _ in range(self.quantum_limit):
            with self.quantum_lock:
                print(f"Quantum {self.current_quantum} starting.")
            
            # Signal all threads to start their work for the quantum
            self.barrier.wait()

            # Simulate logical work for the main thread during the quantum
            self.do_main_work()
            
            # Wait for all threads to finish the quantum
            self.barrier.wait()
            
            with self.quantum_lock:
                print(f"Quantum {self.current_quantum} finished.\n")
                self.current_quantum += 1
    
    def subsystem_task(self, subsystem_id, cpu_id):
        while True:
            # Wait for the quantum to start
            self.barrier.wait()
            
            # Perform work in this quantum
            with self.quantum_lock:
                print(f"Subsystem {subsystem_id} - CPU {cpu_id} working in Quantum {self.current_quantum}")
            
            # Simulate logical work
            self.do_sub_work(subsystem_id, cpu_id)
            
            # Indicate work is complete
            with self.quantum_lock:
                print(f"Subsystem {subsystem_id} - CPU {cpu_id} finished work in Quantum {self.current_quantum}")
            
            # Wait for the quantum to end
            self.barrier.wait()
    
    def do_main_work(self):
        # Perform any logical tasks for the main thread here
        pass

    def do_sub_work(self, subsystem_id, cpu_id):
        # Perform any logical tasks for the subsystems here
        pass

# Create the quantum system
system = QuantumSystem()

# Start the main system thread
main_thread = threading.Thread(target=system.main_system)
main_thread.start()

# Start threads for subsystems
threads = []

# Subsystem 1: 3 CPUs
for cpu_id in range(1, 4):
    threads.append(threading.Thread(target=system.subsystem_task, args=(1, cpu_id)))

# Subsystem 2: 2 CPUs
for cpu_id in range(1, 3):
    threads.append(threading.Thread(target=system.subsystem_task, args=(2, cpu_id)))

# Subsystem 3: 1 CPU
threads.append(threading.Thread(target=system.subsystem_task, args=(3, 1)))

# Start all subsystem threads
for t in threads:
    t.start()

# Wait for the main thread to finish
main_thread.join()
