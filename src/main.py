from system import MainSystem
from task import *

'''
3 3
4 4
4 10
T11 4 1 0 0 1
T12 10 0 1 0 2
T13 20 2 0 0 3
$
T21 10 4 0 0
T22 12 0 4 0
T23 2 1 1 3
$
'''
if __name__ == '__main__':
    sources=[]
    Tasks1=[]
    Tasks2=[]
    Tasks3=[]

    # init
    for i in range(3):
        line=input().split()
        sources.append([int(line[0]),int(line[1])])
    while True:
        line=input()
        sample=line.split()
        if sample[0]== '$':
            break
        Tasks1.append(Sub1Task(sample[0],int(sample[4]),int(sample[1]),[int(sample[2]),int(sample[3])],int(sample[5])))
    #inputs for type Task 2
    while True:
        line=input()
        sample=line.split()
        if sample[0]== '$':
            break
        Tasks2.append(Sub2Task(sample[0],int(sample[4]),int(sample[1]),[int(sample[2]),int(sample[3])]))
    # while True:
    #     line=input()
    #     sample=line.split()
    #     if sample[0]== '$':
    #         break
    #     Tasks3.append(Sub3Task(sample[0],int(sample[4]),int(sample[1]),[int(sample[2]),int(sample[3])],int(sample[5]),int(sample[7])))
    #inputs for type Task 3
    sys = MainSystem({'tasks': Tasks1, 'resources': sources[0]}, {'tasks': Tasks2, 'resources': sources[1]}, {})
    sys.main()
