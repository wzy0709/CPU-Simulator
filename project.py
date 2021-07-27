import queue
import sys
import math
import copy
from queue import Queue
import bisect 

# rand function
class Rand48( object ):
    def srand48( self, seedval ):
        self.Xn = (seedval << 16) + 0x330E
    def drand48(self):
        self.Xn = (0x5DEECE66D * self.Xn + 0xB) & (2 ** 48 - 1)
        return self.Xn / (2 ** 48)
# global variable
rand = Rand48()
# get exponential distribution pseudo-random number
def next_exp():
    r = rand.drand48()
    x = -( math.log(r) ) / lam
    while x>max_bound:
        r = rand.drand48()
        x = -( math.log(r) ) / lam
    return x
# CPU class
class CPU (object):
    def __init__(self, cpu_time, io_time):
        self.cpu_time = cpu_time
        self.io_time = io_time
# process class
class Process( object ):
    def __init__(self, n, arrvial_time):
        self.name = chr(ord('A')+n)
        self.arrival_time = arrvial_time
        self.bursts = []
        self.cw_time = 0
        self.io_time = 0
# create processor
def create_process(n):
    process = Process(n, math.floor(next_exp()))
    num_bursts = math.ceil(rand.drand48()*100)
    #create bursts
    for i in range(num_bursts):
        cpu_time = math.ceil(next_exp())
        if i == num_bursts-1:
            io_time = 0
        else:
            io_time = math.ceil(next_exp())*10
        process.bursts.append(CPU(cpu_time,io_time))
    return process

# get string
def get_string(processes):
    mystr = "[Q"
    if not processes:
        mystr += " empty"
    else:
        for p in processes:
            mystr+=' '
            mystr+=p.name
    mystr += ']'
    return mystr
#FCFS algo
def fcfs(processes):
    current_time = 0
    cpu_total_time = 0
    wait_time = 0
    turnaround = 0
    cpu_working = False
    cpu_time = 0
    cpu_p = None
    io_c = None
    io_p = None
    cpu_q = []
    io_q = []
    cs_count = 0
    print("time %ims: Simulator started for FCFS %s"% (current_time, get_string(cpu_q) ) )
    psort = sorted(processes,key=lambda x:x.arrival_time)
    while 1:
        # new process arrrives
        if psort and current_time==psort[0].arrival_time:
            new_p = psort.pop(0)
            # add to queue
            new_p.cw_time = current_time + context_switch_time/2
            cpu_q.append(new_p)
            if current_time<1000:
                print("time %ims: Process %c arrived; added to ready queue %s"% (current_time, new_p.name, get_string(cpu_q) ) )
        current_time+=1
        # cpu process
        if not cpu_working:
            if len(cpu_q)>1:
                wait_time += (len(cpu_q)-1)
            # context switch satisfies
            if cpu_q and current_time >= cpu_q[0].cw_time:
                # start process the process
                cpu_p = cpu_q.pop(0)
                c = cpu_p.bursts[0]
                cs_count+=1
                cpu_total_time += c.cpu_time
                if current_time<1000:
                    print("time %ims: Process %c started using the CPU for %ims burst %s"% 
                        (current_time, cpu_p.name, c.cpu_time, get_string(cpu_q) ))
                cpu_time = current_time+c.cpu_time
                cpu_working = True
        # check if cpu finishes
        else:
            # cpu finishes
            wait_time += len(cpu_q)
            if current_time== cpu_time:
                cpu_p.cw_time = current_time + context_switch_time/2
                io_c = cpu_p.bursts.pop(0)
                # process finishes
                if len(cpu_p.bursts) == 0:
                    print("time %ims: Process %c terminated %s"%
                        (current_time, cpu_p.name, get_string(cpu_q) ) )
                    turnaround+=(current_time-cpu_p.arrival_time)
                else:
                    # go to i/o
                    io_p = cpu_p
                    io_p.io_time = current_time + io_c.io_time + context_switch_time/2
                    io_q.append(io_p)
                    io_q.sort(key = lambda x:(x.io_time,x.name))
                    if current_time<1000:
                        if len(cpu_p.bursts)==1:
                            print("time %ims: Process %c completed a CPU burst; %i burst to go %s"% 
                                (current_time, cpu_p.name, len(cpu_p.bursts), get_string(cpu_q) ) )
                        else:
                            print("time %ims: Process %c completed a CPU burst; %i bursts to go %s"% 
                                (current_time, cpu_p.name, len(cpu_p.bursts), get_string(cpu_q) ) )
                        print("time %ims: Process %c switching out of CPU; will block on I/O until time %ims %s"% 
                            (current_time, io_p.name, io_p.io_time , get_string(cpu_q) ) )
            # switch finishes
            elif current_time==cpu_p.cw_time:
                cpu_working = False
                if len(cpu_p.bursts) == 0 and not cpu_q and not io_q:
                    #finishes
                    print("time %ims: Simulator ended for FCFS [Q empty]"%(current_time))
                    return [current_time, cpu_total_time, cs_count, wait_time, turnaround]
                elif cpu_q:
                    cpu_q[0].cw_time = current_time + context_switch_time/2
        #i/o finishes
        while io_q and (current_time==io_q[0].io_time):
            io_p = io_q.pop(0)
            io_p.cw_time = current_time + context_switch_time/2
            cpu_q.append(io_p)
            if  current_time<1000:
                print("time %ims: Process %c completed I/O; added to ready queue %s"% 
                    (current_time, io_p.name, get_string(cpu_q) ))

#RR algo
def rr(processes):
    current_time = 0
    cpu_total_time = 0
    wait_time = 0
    turnaround = 0
    cpu_working = False
    cpu_time = 0
    cpu_p = None
    io_c = None
    io_p = None
    cpu_q = []
    io_q = []
    cs_count = 0
    print("time %ims: Simulator started for FCFS %s"% (current_time, get_string(cpu_q) ) )
    psort = sorted(processes,key=lambda x:x.arrival_time)
    while 1:
        # new process arrrives
        if psort and current_time==psort[0].arrival_time:
            new_p = psort.pop(0)
            # add to queue
            new_p.cw_time = current_time + context_switch_time/2
            cpu_q.append(new_p)
            if current_time<1000:
                print("time %ims: Process %c arrived; added to ready queue %s"% (current_time, new_p.name, get_string(cpu_q) ) )
        current_time+=1
        # cpu process
        if not cpu_working:
            if len(cpu_q)>1:
                wait_time += (len(cpu_q)-1)
            # context switch satisfies
            if cpu_q and current_time >= cpu_q[0].cw_time:
                # start process the process
                cpu_p = cpu_q.pop(0)
                c = cpu_p.bursts[0]
                cs_count+=1
                cpu_total_time += c.cpu_time
                if current_time<1000:
                    print("time %ims: Process %c started using the CPU for %ims burst %s"% 
                        (current_time, cpu_p.name, c.cpu_time, get_string(cpu_q) ))
                cpu_time = current_time+c.cpu_time
                cpu_working = True
        # check if cpu finishes
        else:
            # cpu finishes
            wait_time += len(cpu_q)
            if current_time== cpu_time:
                cpu_p.cw_time = current_time + context_switch_time/2
                io_c = cpu_p.bursts.pop(0)
                # process finishes
                if len(cpu_p.bursts) == 0:
                    print("time %ims: Process %c terminated %s"%
                        (current_time, cpu_p.name, get_string(cpu_q) ) )
                    turnaround+=(current_time-cpu_p.arrival_time)
                else:
                    # go to i/o
                    io_p = cpu_p
                    io_p.io_time = current_time + io_c.io_time + context_switch_time/2
                    io_q.append(io_p)
                    io_q.sort(key = lambda x:(x.io_time,x.name))
                    if current_time<1000:
                        if len(cpu_p.bursts)==1:
                            print("time %ims: Process %c completed a CPU burst; %i burst to go %s"% 
                                (current_time, cpu_p.name, len(cpu_p.bursts), get_string(cpu_q) ) )
                        else:
                            print("time %ims: Process %c completed a CPU burst; %i bursts to go %s"% 
                                (current_time, cpu_p.name, len(cpu_p.bursts), get_string(cpu_q) ) )
                        print("time %ims: Process %c switching out of CPU; will block on I/O until time %ims %s"% 
                            (current_time, io_p.name, io_p.io_time , get_string(cpu_q) ) )
            # switch finishes
            elif current_time==cpu_p.cw_time:
                cpu_working = False
                if len(cpu_p.bursts) == 0 and not cpu_q and not io_q:
                    #finishes
                    print("time %ims: Simulator ended for FCFS [Q empty]"%(current_time))
                    return [current_time, cpu_total_time, cs_count, wait_time, turnaround]
                elif cpu_q:
                    cpu_q[0].cw_time = current_time + context_switch_time/2
        #i/o finishes
        while io_q and (current_time==io_q[0].io_time):
            io_p = io_q.pop(0)
            io_p.cw_time = current_time + context_switch_time/2
            cpu_q.append(io_p)
            if  current_time<1000:
                print("time %ims: Process %c completed I/O; added to ready queue %s"% 
                    (current_time, io_p.name, get_string(cpu_q) ))

# output
def output(ret, processes):
    [total_time, cpu_time, cs_count, wait_time, turnaround] = ret
    output = 'Algorithm FCFS\n'
    turnaround = cpu_time+ (cs_count*context_switch_time)+wait_time
    bur_count = 0
    for p in processes:
        bur_count+=len(p.bursts)
    line = "-- average CPU burst time: %.3f ms\n"%(cpu_time/bur_count)
    output+=line
    line = "-- average wait time: %.3f ms\n"%(wait_time/bur_count)
    output+=line
    line = "-- average turnaround time: %.3f ms\n"%(turnaround/bur_count)
    output+=line
    line = "-- total number of context switches: %i\n"%(cs_count)
    output+=line
    line = "-- total number of preemptions: 0\n"
    output+=line
    line = "-- CPU utilization: %.3f"%((cpu_time/total_time)*100)
    line += '%\n'
    output+=line
    return output

if ( __name__ == "__main__" ):
    # if(len(sys.argv)!=8):
    #     print("ERROR: wrong input number\n",file=sys.stderr)
    # n = int(sys.argv[1])
    # seed = int(sys.argv[2])
    # lam = float(sys.argv[3])
    # max_bound = int(sys.argv[4])
    # tcs = int(sys.argv[5])
    # alpha = float(sys.argv[6])
    # tslice = int(sys.argv[7])
    global seedval
    global max_bound
    global lam
    global context_switch_time
    num_process = 16
    seedval = 2
    lam = 0.01
    max_bound = 256
    context_switch_time = 4
    alpha = 0.75
    tslice = 64
    #set seed
    r = rand.srand48( seedval )
    #create process
    processes = []
    for i in range(num_process):
        processes.append(create_process(i))
        print("Process %c (arrival time %i ms) %i CPU bursts (tau %ims)" %
                (processes[i].name, processes[i].arrival_time, len(processes[i].bursts), 1/lam))
    print('')
    file = open("simout.txt","a+")
    ret = fcfs(copy.deepcopy(processes))
    file.write(output(ret, processes))
    ret = rr(copy.deepcopy(processes))
    file.write(output(ret, processes))
    file.close()
    