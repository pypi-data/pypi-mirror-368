
import threading
from .LOG import LOG
from .PARALLEL_THREAD import  PARALLEL_THREAD
from .PRINTABLE import  PRINTABLE
from .STRUCT import  STRUCT
from .TESTS import  TESTS
from .UTILS import  UTILS


class PARALLEL_THREAD_POOL(PRINTABLE, STRUCT): 
# Keep the order PRINTABLE, STRUCT so that PRINTABLE overrides the ToYaml method.


    ICON= '🏎️'


    def __init__(self, 
        name:str= None,
        seconds:int= None,
        maxWorkers:int= 30,
        continueMethod:callable= None,
        raiseException:bool= True,
        goUp:int=0
    ) -> None:
        
        # We need at least one attribute to initialize the parent class.
        STRUCT.__init__(self, {
            'addedTasks': [],
            'addedTaskNames': []
        })

        LOG.Print(self.__init__, dict(
            name= name,
            seconds= seconds,
            maxWorkers= maxWorkers,
            continueMethod= continueMethod
        ))

        self._raiseException = raiseException
        self._name = name

        self._log = LOG.PARALLEL().LogProcess(
            name= self._name, 
            goUp= goUp+1)

        #self._display = PARALLEL_DISPLAY(maxWorkers)
        self._maxWorkers = maxWorkers
        self._continueMethod = continueMethod or self._DefaultRunnerContinueMethod
        self._tasks:list[PARALLEL_THREAD] = []
        self._timeout = seconds or 3
        self._startTime = UTILS.TIME().Now()
        self._lock = threading.Lock()
        self._waiting:list[PARALLEL_THREAD] = None

        PRINTABLE.__init__(self, toJson=self.ToJson)


    def ToJson(self):
        return dict(
            Name= self._name,
            #Timeout= self.GetTimeout(),
            #CurrentDurationInSeconds= self.GetCurrentDurationInSeconds(),
            #HasPendingThreads= self.HasPendingThreads(),
            #HasNoErrors= self.HasNoErrors(),
            #ContinueRun= self.ContinueRun(),
            #AddedThreadNames= self.GetAddedThreadNames(),
            #AddedThreads= self.GetAddedThreads()
        )


    def __enter__(self):
        return self
    

    def __exit__(self, exc_type, exc_value, traceback):
        
        try:
            # Run all tasks, if the developer forgot to run them.
            if exc_type:
                LOG.Print(self.__exit__, f': An exception occurred: {exc_type}', exc_value)
            else:
                LOG.Print(self.__exit__, f': No exceptions occurred.')
                if self._log.IsPending():
                    LOG.Print(self.__exit__, f': Running all tasks.')
                    self.RunAllThreads()

        finally:
            # Stop accepting log messages, dump the log, and add an icon.
            self._log.Stop()


    def __to_json__(self):
        return dict(
            Name= self._name,
            Timeout= self.GetTimeout(),
            CurrentDurationInSeconds= self.GetCurrentDurationInSeconds(),
            HasPendingThreads= self.HasPendingThreads(),
            HasNoErrors= self.HasNoErrors(),
            ContinueRun= self.ContinueRun(),
            GetAddedThreadNames= self.GetAddedThreadNames(),
            GetAddedThreads= self.GetAddedThreads())


    def LOCK(self, timeout:int=3):
        '''👉️ Returns the parallel lock.'''
        from .PARALLEL_LOCK import  PARALLEL_LOCK
        return PARALLEL_LOCK(self._lock, timeout=timeout)


    def GetLog(self):
        '''👉️ Returns the log buffer.'''
        return self._log
    
    
    def _DefaultRunnerContinueMethod(self, *args):
        '''👉️ Default continue method.'''
        return True


    def GetTimeout(self):
        '''👉️ Returns the timeout.'''
        return self._timeout


    def GetCurrentDurationInSeconds(self):
        '''👉️ Returns the duration in seconds.'''
        return UTILS.TIME().GetDurationInSeconds(
            self._startTime, 
            UTILS.TIME().Now())


    def HasTimedOut(self):
        '''👉️ Checks if the runner has timed out.'''

        if self._timeout == None:
            return False

        if self.GetCurrentDurationInSeconds() > self._timeout:
            return True

        return False


    def RunThread(self,
        handler:callable,
        name:str= None,
        goUp:int=0
    ):
        '''👉️ Runs a single task.'''
        return self.RunThreadList(
            handlers= [handler],
            names= [name],
            goUp= goUp+1)
            


    def RunThreadList(self, 
        handlers:list[callable], 
        names:list[str]= None,
        ensureSubRunner:bool= False,
        parallel:bool= True,
        goUp:int=0
    ):
        '''👉️ Adds a list of tasks to the runner.'''

        if not parallel:
            # Run the tasks in sequence.
            for handler in handlers:
                LOG.Print(f'\n🏃‍ Running {handler.__qualname__}')

                thread = PARALLEL_THREAD(
                    handler= handler,
                    name= names.pop(0) if names else handler.__name__,
                    goUp= goUp+1)

                from .PARALLEL_THREAD_WRAPPER import  PARALLEL_THREAD_WRAPPER
                PARALLEL_THREAD_WRAPPER.Wrap(
                    thread = thread,
                    pool= self)
                
                if thread.HasFailed():
                    e = thread.GetException()
                    self._log.SetFail(e)
                    raise e
                
            return self
        
        # Run the tasks in parallel.
        for handler in handlers:
            self.AddThread(
                name= names.pop(0) if names else None,
                handler= handler, 
                ensureSubRunner= ensureSubRunner,
                goUp= goUp+1)
            
        self.RunAllThreads(
            ensureSubRunner=ensureSubRunner)
        
        return self


    def GetSortedAddedThreadNames(self):
        tasks = self.GetAddedThreadNames()
        tasks = UTILS.SortList(tasks)
        return tasks


    def GetAddedThreadNames(self):
        return self.GetList('addedTaskNames', itemType=str)
    

    def GetAddedThreads(self) -> list[PARALLEL_THREAD]:
        tasks = self.GetList('addedTasks', itemType=PARALLEL_THREAD)
        return tasks


    def AddThread(self,
        handler:callable,
        args:dict[str, any]= {},
        name:str= None,
        continueMethod:callable= None,
        ensureSubRunner:bool= False,
        goUp:int=0
    ):
        '''👉️ Adds a task to the runner.
        
        Arguments:
        * `name` {str} -- The unique description of the task for the user.
        * `handler` {callable} -- The method to invoke.
        * `args` {dict[str, any]} -- The arguments to pass to the method.
        * `continueMethod` {callable} -- The method to check if the task should continue running.
        '''
        LOG.Print(self.AddThread, f'[{name}]')
        
        if name == None:
            name = handler.__name__

        if name in self.ListStr('addedTaskNames'):
            LOG.RaiseValidationException(f'Thread [{name}] already exists.', self)
        
        self.AppendToAtt('addedTaskNames', name)
        self.GetList('addedTaskNames', itemType=str)

        thread = PARALLEL_THREAD(
            handler= handler,
            name= name,
            taskArgs= args,
            continueMethod= continueMethod,
            goUp= goUp+1)
        
        if thread == None:
            LOG.RaiseException('Invalid parallelTask == None')

        self.AppendToAtt('addedTasks', thread)
        self.GetList('addedTasks', itemType=PARALLEL_THREAD)

        # Check if we're already running.
        #with self.LOCK(timeout=2):
        if self._waiting != None:
            # If we're already running, add to the waiting list.
            self._waiting.append(thread)
        else:
            # Otherwise, add to the tasks list.
            if ensureSubRunner:
                LOG.RaiseException(f'[{name}]: We should not be here!')
            self._tasks.append(thread)

        return thread


    def ContinueRun(self):
        return self._continueMethod()

    

    def HasPendingThreads(self):
        '''👉️ Indicates if there are tasks that have not been run.'''
        for task in self.GetAddedThreads():
            if task.IsPending() or task.IsRunning():
                return True
        return False


    def HasNoErrors(self):
        '''👉️ Indicates if there have been no errors so far.'''
        for task in self.GetAddedThreads():
            if task.HasJoined() and task.HasFailed():
                return False
        return True


    def RunAllThreads(self, ensureSubRunner:bool=False):
        '''👉️ Executes tasks in parallel.
        
        Example:
            ```python
            from functools import partial
            UTILS.OS().Parallel([
                partial(myFunc, myParam1=val11, myParam2=val12),
                partial(myFunc, myParam1=val21, myParam2=val22)
            ])
            ```
        '''
        LOG.Print(self.RunAllThreads, self)

        self._log.SetRunning()

        # Check if we're already running.
        # In theory, tasks should be added before running.
        if self._waiting != None:
            LOG.Print(self.RunAllThreads, f': Already running.')
            return
            
        if ensureSubRunner:
            LOG.RaiseException('We should not be here!')

        # Ensure we're ready to run.
        if not self.ContinueRun():
            LOG.RaiseException(f'@: Continue method returned False.')

        # Ensure there are tasks to run.
        if len(self._tasks) == 0:   
            LOG.Print(self.RunAllThreads, f': No tasks to run.')
            self._log.SetDone()
            return

        # Copy the tasks into a waiting list.
        with self.LOCK():
            self._waiting:list[PARALLEL_THREAD] = []

            # Move all the tasks to the waiting list.
            while len(self._tasks) > 0:
                task = self._tasks.pop()
                self._waiting.append(task)
                
            # Sort the list by task description
            self._waiting = UTILS.SortList(
                self._waiting, key= PARALLEL_THREAD.GetName)


        def _RunThreads():

            # Run the tasks in parallel
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(
                max_workers= self._maxWorkers
            ) as executor:
                
                try:

                    futures = []
                    
                    # Execute all tasks without dependencies.
                    def CheckWaiting():
                        while len(self._waiting) > 0 \
                        and self.HasNoErrors() \
                        and self.ContinueRun():

                            # Confirm if we've timed out.
                            if self.HasTimedOut():
                                timeout = self.GetTimeout()
                                duration = self.GetCurrentDurationInSeconds()
                                LOG.RaiseException(f'@'
                                    f': Timeout of {timeout}s'
                                    f' reached after {duration} secs. '
                                    f' {(len(self._waiting) > 0)=}'
                                    f' {self.HasNoErrors()=}'
                                    f' {self.ContinueRun()=}', self)

                            # Loop the pending task queue.
                            for task in self._waiting:

                                # Check if the tasks can be executed.
                                if not task.Continue():
                                    continue

                                # Remove from the pending queue.
                                self._waiting.remove(task)

                                # Execute the task.
                                from .PARALLEL_THREAD_WRAPPER import  PARALLEL_THREAD_WRAPPER
                                future = executor.submit(
                                    PARALLEL_THREAD_WRAPPER.Wrap, 
                                    task, self)
                                task.SetFuture(future)

                                # Add the future to the list, to get the results.
                                futures.append(future)
                                
                            # Wait a bit before checking again.
                            UTILS.Sleep(0.1)

                    def CheckFutures():
                        # Wait for all tasks to finish.
                        while self.HasPendingThreads() \
                        and self.HasNoErrors() \
                        and self.ContinueRun():
                            
                            CheckWaiting()

                            LOG.Print(f'@: WaitingForTasks', self)
                            for future in futures:
                                future.result()
                            LOG.Print(f'@: WaitingForTasks.Done', self)

                            # Stop here if done.
                            if not (
                                self.HasPendingThreads() \
                                and self.HasNoErrors() \
                                and self.ContinueRun()
                            ):
                                break

                            # Confirm if we've timed out.
                            if self.HasTimedOut():
                                LOG.RaiseException('@'
                                    f': Timeout of {self.GetTimeout()}s'
                                    f' reached after {self.GetCurrentDurationInSeconds()} secs. '
                                    f' {self.HasPendingThreads()=} '
                                    f' {self.HasNoErrors()=} '
                                    f' {self.ContinueRun()=}', 
                                    self)
                                
                            UTILS.Sleep(0.1)

                    CheckFutures()

                    # Get the results.
                    results = {}
                    for future in futures:
                        task = future.result()
                        if not task:
                            raise Exception('Invalid state')
                        if task:
                            key = task['Task']
                            results[key] = task['Result']
                        LOG.Print(f'🏎️ @.Result:', task)

                    '''
                    for task in self.GetAddedTasks():
                        result = task._future.result()['Result']
                        key = task.GetDescription()
                        results[key] = result
                    '''

                    LOG.Print(f'@.Result:', results)
                    
                    # Ensure the results included all added tasks.
                    if self.HasNoErrors():
                        TESTS.AssertEqual(
                            STRUCT(results).SortedKeys(),
                            self.GetSortedAddedThreadNames())

                except Exception as e:
                    LOG.Print(f"@: An error occurred: {e}", e)
                    raise

                finally:
                    # Clear the waiting list to allow for others to run.
                    with self.LOCK():
                        self._waiting = None

            # Check if any exceptions were raised.
            self.RaiseExceptions()

            # Return the results.
            LOG.Print(f'@: AllTasks: results', results)
            return STRUCT(results)
        

        # Mute the console prints.
        try:
            preMuteConsole = LOG.Settings().GetMuteConsole()
            LOG.Settings().SetMuteConsole(True)
            self._log.DumpToFile()
            
            # Run the tasks.
            ret = _RunThreads()

            # Update the icon in the directory.
            self._log.SetDone()

            return ret
        
        except Exception as e:
            self._log.SetFail(e)
            if self._raiseException:
                raise

        finally:
            self._log.Stop()
            LOG.Settings().SetMuteConsole(preMuteConsole)
            #self._display.ClearScreen()


    def DeleteLogFiles(self, reason:str):
        '''👉️ Deletes the log files.'''
        for task in self._tasks:
            if not task.IsDone():
                LOG.RaiseValidationException(
                    f'Thread [{task.GetName()}] is not done.'
                    f' Should not delete a log file that is not done.', task)
            task.GetLog().Delete(reason=reason)
        self._log.Delete(reason=reason)


    def RaiseExceptions(self):
        '''👉️ Raises exceptions if any.'''
        
        self._log.RaiseExceptions()
        
        for task in self.GetAddedThreads():
            if task.HasJoined():
                if task.HasFailed():
                    raise task.GetException()

        if self.HasPendingThreads():
            LOG.RaiseException('There are still pending tasks.')