from multiprocessing import Manager 

manager = None

def createManager():
    global manager
    if manager is None:
        manager = Manager()
    return manager

def getManager():
    return manager