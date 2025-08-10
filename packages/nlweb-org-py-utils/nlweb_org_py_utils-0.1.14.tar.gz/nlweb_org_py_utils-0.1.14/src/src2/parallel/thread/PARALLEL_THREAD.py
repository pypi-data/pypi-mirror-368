from LOG import LOG
from PRINTABLE import  PRINTABLE
from UTILS import  UTILS

class PARALLEL_THREAD(PRINTABLE):
    '''👉️ Initializes a task to be run in parallel.'''

    ICON = '🏎️'

    def __init__(self, 
        name:str,
        handler:callable,
        taskArgs:dict[str,any] = {},
        continueMethod:callable=None,
        goUp:int=0
    ): 
        LOG.Print(self.__init__)

        from UTILS import  UTILS
        UTILS.AssertIsCallable(handler, require=True)
        UTILS.AssertIsAnyType(taskArgs, [dict], require=False)
        UTILS.AssertIsStr(name, require=True)
        UTILS.AssertIsCallable(continueMethod, require=False)

        self._result = '<PENDING TO RUN>'
        self._task = handler
        self._name = name
        self._args = taskArgs
        self._continueMethod = continueMethod or self._DefaultTaskContinueMethod

        self._hasJoined = False
        self._hasFailed = False
        self._hasStarted = False

        # Call the log buffer path.
        log = LOG.PARALLEL().CreateBuffer(
            name= name, 
            goUp= goUp+1)
        self._logPath = log.GetPath()
        log.Delete(reason='PARALLEL_THREAD')

        # Define the serialization for logging.
        super().__init__(lambda: {
            'Description': self.GetName(),
            'Result': self.GetResult(),  
        })
        

    def HasJoined(self):
        '''👉️ Returns True if the task has joined.'''
        return self._hasJoined


    def HasFailed(self):
        '''👉️ Returns True if the task failed.'''
        if not self._hasStarted:
            LOG.RaiseException('Thread not started!')
        if not self._hasJoined:
            LOG.RaiseException('Thread still running!')
        return self._hasFailed  
    

    def GetException(self):
        '''👉️ Returns the exception of the task.'''
        return self._exception
    

    def SetStarted(self):
        '''👉️ Sets the task as started.'''
        LOG.Print(self.SetStarted, self)
        self._hasStarted = True


    def SetDone(self, result):
        '''👉️ Sets the task as done.'''
        LOG.Print(self.SetDone, result, self)
        self._hasJoined = True
        self._result = result


    def SetFailed(self, exception:Exception):
        '''👉️ Sets the task as failed.'''
        LOG.Print(self.SetFailed, exception, self)
        self._hasJoined = True
        self._hasFailed = True
        self._exception = exception

    
    def IsDone(self):
        '''👉️ Returns True if the task is done.'''
        if not self._hasStarted:
            LOG.RaiseException('Thread not started!')
        if not self._hasJoined:
            LOG.RaiseException('Thread still running!')
        return not self._hasFailed


    def IsRunning(self):
        '''👉️ Returns True if the task is running.'''
        if not self._hasStarted:
            LOG.RaiseException('Thread not started!')
        return not self._hasJoined
    

    def IsPending(self):
        '''👉️ Returns True if the task is pending.'''
        return not self._hasStarted


    def GetStatus(self):
        '''👉️ Returns the task status.'''
        if self.IsPending():
            return 'PENDING'
        if self.IsRunning():
            return 'RUNNING'
        if self.HasFailed():
            return 'FAILED'
        if self.IsDone():
            return 'DONE'
    
    
    def _DefaultTaskContinueMethod(self, *args):
        '''👉️ Default continue method.'''
        return True


    def GetName(self):
        '''👉️ Returns the task description.'''
        return self._name


    def Continue(self):
        '''👉️ Returns True if the task can run.'''
        from PYTHON_METHOD import  PYTHON_METHOD
        return PYTHON_METHOD(
            self._continueMethod
        ).InvokeWithMatchingArgs(
            args= self._args)
    
    

    def GetResult(self):
        return self._result
    

    def SetFuture(self, future):
        self._future = future


    def GetFuture(self):
        return self._future
            