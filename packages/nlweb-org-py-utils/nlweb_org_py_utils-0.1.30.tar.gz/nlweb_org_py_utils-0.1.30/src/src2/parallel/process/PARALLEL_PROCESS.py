from __future__ import annotations
from .LOG import LOG
from .PARALLEL_PROCESS_WRAPPER import PARALLEL_PROCESS_WRAPPER
from .PRINTABLE import  PRINTABLE


class PARALLEL_PROCESS(PRINTABLE):
    '''👉️ A process.'''

    ICON = '👷'

    def __init__(self, 
        handler:callable, 
        pool:any,
        args:list|dict= {}, 
        name:str = None,
        onJoin:callable = None,
        onDone:callable = None,
        goUp:int = 0
    ) -> None:
        '''👉️ Initialize the process.
            * name: The name of the process (defaults to the handler's name).
            * baseLogDir: The base directory for the logs.
            * handler: The function to run.
            * args: The arguments to pass to the function.
            * onJoin: The function to run when the process completes.
        '''

        LOG.Print(self.__init__, f'[{name}]',
            dict(
                handler= handler,
                args= args,
                name= name,
                onJoin= onJoin))
        
        # Ensure the parameters.
        from .UTILS import  UTILS
        UTILS.AssertIsCallable(handler, require=True)
        UTILS.AssertIsAnyType(args, [dict,list], require=False)
        UTILS.AssertIsStr(name, require=False)
        
        # Set the pool.
        from .PARALLEL_PROCESS_POOL import PARALLEL_PROCESS_POOL
        UTILS.AssertIsType(pool, PARALLEL_PROCESS_POOL, require=False)
        self._pool:PARALLEL_PROCESS_POOL = None
        if pool: self._pool = pool or PARALLEL_PROCESS_POOL
        
        self._name = name

        # Set the handler and arguments.
        self._hasJoined = False
        self._hasStarted = False
        self._result = None
        self._handler = handler
        self._args = args
        self._onJoin:callable = onJoin
        self._onDone:callable = onDone
        self._share:dict = None
        self._processID = None
        self._exceptionType = None
        self._exceptionMessage = None

        #logName = f'{name}.{handler.__name__}'
        #if pool: logName = f'{pool.GetName()}.{logName}' 
        #logName.replace('None.', '')

        # Get the path to the log buffer.
        log = LOG.PARALLEL().CreateBuffer(
            name= name or handler.__name__,
            goUp= goUp+1)
        self._logPath = log.GetPath()
        log.Delete(reason='PARALLEL_PROCESS')
        
        # Set up the serialization to json.
        super().__init__(self.ToJson)


    def __enter__(self):
        return self
    

    def __exit__(self, exc_type, exc_value, traceback):
        LOG.Print(self.__exit__, exc_type, exc_value, self)  


    def ToJson(self):
        '''👉️ Return the JSON representation of the object.'''
        ret = dict(
            Name= self._name,
            Handler= self._handler.__name__,
            Args= self._args,
            LogPath = self._logPath,
            ProcessID= self._processID,
            HasStarted= self._hasStarted,
            HasJoined= self._hasJoined,
            HasException= self.HasException(),
            ExceptionType= self._exceptionType,
            ExceptionMessage= self._exceptionMessage,
            Result= self._result,)

        return ret


    def GetName(self):
        '''👉️ Return the name of the process.'''
        return self._name


    def HasException(self):
        '''👉️ Return True if the process has an exception.'''
        return self._exceptionType != None


    def RaiseException(self):
        '''👉️ Raises all exceptions in the process.'''
        if self.HasException():
    
            LOG.RaiseValidationException(f'@:'
                f' {self._exceptionMessage or '?'} at [{self._handler.__name__}]', dict(
                    Type= self._exceptionType,
                    Message= self._exceptionMessage))

    
    def Start(self):
        '''👉️ Start the process.'''

        LOG.Print(self.Start, f'[{self._name}]', self)

        # Verify if the process has already been started.
        if self._hasStarted:
            LOG.RaiseException('The process has already been started.')
        self._hasStarted = True

        import multiprocessing

        # Create a shared memory object.
        manager = multiprocessing.Manager()
        self._share = manager.dict(
            Result= None,
            Status= None,
            ExceptionType= None,
            ExceptionMessage= None)

        # Create a process.
        self._process = multiprocessing.Process(
            target= PARALLEL_PROCESS_WRAPPER.Wrap,
            args= (
                self._name, 
                self._handler, 
                self._args, 
                self._share,
                self._logPath,
                LOG.Settings().GetWriteToConsole(),
                LOG.Settings().GetTestFast(),
                self._onDone or self._pool._onDone
            ))
        
        # Run the process.
        self._process.start() # Start the process
        self._processID = self._process.ident
        
        from .PARALLEL_PROCESSES import PARALLEL_PROCESSES
        PARALLEL_PROCESSES.RegisterProcess(self, 
            processID= self._process.ident)
    
        return self


    def _SetJoined(self):
        self._hasJoined = True

    def HasJoined(self):
        '''👉️ Return True if the process has joined.'''
        return self._hasJoined == True


    def SetResult(self, result):
        '''👉️ Set the result of the process.'''
        LOG.Print(self.SetResult, result, self)
        self._result = result


    def GetResult(self):    
        '''👉️ Return the result of the process.
        * If the process is pending, it will be started and joined.'''
        LOG.Print(self.GetResult, f'[{self._name}]', self)

        if self._hasJoined == False:
            return self.Join()
        elif self.HasException():
            raise self.RaiseException()
        else:
            return self._result    
        

    def Join(self):
        '''👉️ Wait for the process to finish and return the result.'''

        LOG.Print(self.Join, self)

        # Verify if the process has been started.
        if not self._hasStarted:
            LOG.Print(self.Join, f': The process has not been started.', self)
            return self.Start().Join()

        # Verify if the process has already been joined.
        if self._hasJoined:
            LOG.Print(self.Join, f': The process has already been joined.')
            return self.GetResult()
        
        self._SetJoined()

        # Run the onJoin function.
        if self._onJoin:
            self._onJoin(self)

        # Wait for the process to complete
        result:any = None
        try: 
            self._process.join() 
            LOG.Print(self.Join, 
                f'joined with share', 
                dict(self._share), self)
            
            # Check self._process for errors.
            if self._process.exitcode != 0:
                LOG.Print(self.Join, f'[{self._name}]: exit code', self._process.exitcode, self)
                raise Exception(f'Process failed with exit code {self._process.exitcode}')

            if self._share['Status'] == 'FAILED':
                LOG.Print(self.Join, f'[{self._name}]: failed', self)
                self._exceptionMessage = self._share['ExceptionMessage']
                self._exceptionType = self._share['ExceptionType']
                self.RaiseException()

            if self._share['Status'] == 'DONE':
                LOG.Print(self.Join, f'[{self._name}]: done', self)
                pass
            
            result = self._share['Result']
            self.SetResult(result)

            LOG.Print(self.Join, f'[{self._name}]: return', result, self)
            return result
        
        except Exception as e:
            LOG.Print(self.Join, f'[{self._name}]: exception', e, self)
            self._exceptionMessage = str(e)
            self._exceptionType = type(e).__name__
            
            #TODO uncomment
            #self.RaiseException()
        

    def Run(self):
        '''👉️ Run the process and return the result.'''
        LOG.Print(f'👷 PARALLEL.PROCESS[{self._name}].Run()')
        self.Start()
        return self.Join()