from .LOG import LOG
from .LOG_BUFFER import LOG_BUFFER


class PARALLEL_PROCESS_WRAPPER:

    ICON = '👷'

    
    @classmethod
    def Wrap(cls,
        name:str, 
        handler:callable, 
        args:dict, 
        share:dict, 
        logPath:str,
        writeToConsole:bool,
        testFast:bool,
        onDone:callable
    ):
        '''👉️ Runs inside a child process.'''
      
        # Load imports
        import sys
        sys.path.append('tests/Imports')
        from .IMPORTS import IMPORTS # don't delete.

        #TODO: uncomment
        #from .AWS_TEST import AWS_TEST
        #AWS_TEST.SetDomain(domain='*')

        # Create the log buffer.
        log = LOG.PARALLEL().CreateBuffer(path= logPath)
        LOG.PARALLEL().LogProcess(name= name, buffer= log)
        LOG.Settings().SetWriteToConsole(writeToConsole)
        LOG.Settings().SetTestFast(testFast)
        
        # Print the first log message after creating the log buffer. 
        LOG.Print(cls.Wrap, dict(
            name= name,
            handler= handler,
            args= args))
        
        status = 'RUNNING'
        try:
            cls._Run(
                handler= handler, 
                args= args, 
                share= share,
                log= log)
            
            LOG.Print(cls.Wrap, ': executed')
            LOG.Print(cls.Wrap, ': share', dict(share))
            status = 'DONE'

        except Exception as e:
            LOG.Print(cls.Wrap, ': failed', e)
            status = 'FAILED'

        finally:
            LOG.Print(cls.Wrap, ': finally')
            log.Stop()

            if onDone and status == 'DONE':
                onDone(name= name)
        

    @classmethod
    def _Run(cls,
        handler:callable, 
        args:dict, 
        share:dict,
        log:LOG_BUFFER
    ):
        # Invoke the handler
        ret = None
        try:
            from .PYTHON_METHOD import  PYTHON_METHOD
            ret = PYTHON_METHOD(
                handler
            ).InvokeWithMatchingArgs(
                args= args)
            
            LOG.Print(cls._Run, ': done', dict(result= ret))
            
            share['Status'] = 'DONE' 
            log.SetDone()

        except Exception as e:
            share['Status'] = 'FAILED' 
            log.SetFail(e)
            
            try:
                share['ExceptionMessage'] = str(e)
                share['ExceptionType'] = type(e).__name__
            except Exception as e:
                # Potential concurrent exception
                #   AttributeError: 'ForkAwareLocal' object has no attribute 'connection'
                #   During handling of the above exception, another exception occurred:    
                if type(e).__name__ == 'FileNotFoundError:': pass
                if type(e).__name__ == 'AttributeError': pass
                raise
        
        # Return the result.
        LOG.Print(cls._Run, f': returning the result', ret)
        
        try:
            share['Result'] = ret
        except Exception as e:
            # Potential concurrent exception
            if type(e).__name__ == 'FileNotFoundError:': pass
            if type(e).__name__ == 'AttributeError': pass
            raise e
        