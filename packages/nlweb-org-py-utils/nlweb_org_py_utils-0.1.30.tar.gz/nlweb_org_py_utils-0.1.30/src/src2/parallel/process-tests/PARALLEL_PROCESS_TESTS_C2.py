from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST
from .TESTS import  TESTS


class PARALLEL_PROCESS_TESTS_C2(PARALLEL_TEST):

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
            
        LOG.PARALLEL().SetClassDone(
            validator= lambda files: self.AssertDirLogFiles(
                files= files,
                prefix= '🔴 PARALLEL_PROCESS_TESTS_C2.',
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
        
        # Same as C1, but with an error.
        # Same as C3, but with parallel= False
        cls().TestProcessWithThreadError(parallel= True)

        LOG.PARALLEL().SetClassDone()