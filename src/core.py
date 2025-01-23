from task import Task

class Core:

    running_task: Task = None

    def __init__(self, name):
        self.name = name
        
    def __str__(self) -> str:
        return f'{self.name}: {self.running_task.name if self.running_task else 'Idle'}'
    
    def run(self):
        
        pass