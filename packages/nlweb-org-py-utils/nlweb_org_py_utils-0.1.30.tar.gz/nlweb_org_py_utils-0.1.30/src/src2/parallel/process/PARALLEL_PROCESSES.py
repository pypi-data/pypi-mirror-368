from .PARALLEL_PROCESS import PARALLEL_PROCESS
from .LOG import LOG

class PARALLEL_PROCESSES:

    ICON = '🏭'
    
    _processes:dict[str,PARALLEL_PROCESS] = {}


    @classmethod
    def RegisterProcess(cls, 
        process:PARALLEL_PROCESS, 
        processID:str
    ):
        '''👉️ Register a process.'''
        LOG.Print(cls.RegisterProcess, f'({processID})', process)
        cls._processes[processID] = process


    @classmethod
    def GetCurrentProcess(cls):
        '''👉️ Return the current process.
        * Returns None if the process is not registered.
        * If None, it means that this is the main process.
        '''
        processID = cls.GetCurrentProcessID()
        if processID not in cls._processes:
            return None
        return cls._processes[processID]


    @classmethod
    def GetCurrentProcessID(cls) -> int:
        '''👉️ Returns the process ID.'''
        import os
        return os.getpid()
    

    @classmethod
    def GetCurrentLogDir(cls):
        '''👉️ Returns the current log directory.'''
        
        # If there's a current child process, return the process's log directory.
        process = cls.GetCurrentProcess()
        if process:
            return process.GetLogDir()
        else:
            return cls.GetDefaultLogDir()
            

    @classmethod
    def GetDefaultLogDir(cls):
        '''👉️ Returns FILESYSTEM.DIRECTORY(__dumps__/PARALLEL/__main__)'''
        from .PARALLEL import  PARALLEL
        return PARALLEL.GetLogDir().GetSubDir('[pp]__main__').Touch()