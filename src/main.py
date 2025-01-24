from system import MainSystem
from task import *

if __name__ == '__main__':
    sources=[]
    Tasks=[]
    # init
    for i in range(3):
        line=input().split()
        sources.append([int(line[0]),int(line[1])])
    while True:
        line=input()
        sample=line.split()
        if sample[0]== '$':
            break
        Tasks.append(Sub1Task(sample[0],int(sample[4]),int(sample[1]),[int(sample[2]),int(sample[3])],int(sample[5])))
        
    sys = MainSystem({'tasks': Tasks, 'resources': sources[0]}, {}, {})
    sys.main()