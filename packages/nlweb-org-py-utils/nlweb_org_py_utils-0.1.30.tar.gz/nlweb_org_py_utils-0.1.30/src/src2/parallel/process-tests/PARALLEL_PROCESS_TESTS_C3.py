from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST
from .TESTS import  TESTS


class PARALLEL_PROCESS_TESTS_C3(PARALLEL_TEST):

    ICON = '🧪'


    def Thread(self):
        LOG.Print('Inside the thread..')
        print(1/0)
        

    def Process(self, parallel:bool = True):
        with PARALLEL.THREAD_POOL() as pool:
            pool.RunThreadList(
                handlers=[self.Thread], 
                parallel= parallel)


    def TestProcessWithThreadError(self, parallel:bool = True):

        with TESTS.AssertValidation():
            with PARALLEL.PROCESS_POOL() as pool:
                pool.StartProcess(
                    handler= self.Process,
                    args= dict(
                        parallel= parallel))
            
        # Raise as a validator, to keet the path valid in the stack trace.
        LOG.PARALLEL().SetClassDone(
            validator= lambda files: self.AssertDirLogFiles(
                files= files,
                prefix= '🔴 PARALLEL_PROCESS_TESTS_C3.',
                fileNames= [
                    'Process.Thread',
                    'Process',
                    'TestProcessWithThreadError.Process',
                    'TestProcessWithThreadError'
                ]))
        

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''
        
        LOG.Print(cls.TestAll)
        
        # Same as C2, but with parallel= False
        cls().TestProcessWithThreadError(parallel= False)

        LOG.PARALLEL().SetClassDone()