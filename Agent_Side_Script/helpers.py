def mean(l):
    return float(sum(l)) / max(len(l), 1)

def getCPU(x):
    return float(x['KernelTime']-x['IdleTime'])/x['UserTime']

def getCPUAvg(l):
    return mean(map(getCPU, l))