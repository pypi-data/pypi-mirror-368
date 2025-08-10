from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST
from .TESTS import  TESTS


class PARALLEL_THREAD_TESTS_2(PARALLEL_TEST):

    ICON = '🧪'


    def Handler(self, val:int):
        self.total += val


    def TestExecution(self):
        
        self.total = 0

        # With with: the threads are automatically executed.
        with PARALLEL.THREAD_POOL() as pool:
            pool.AddThread(
                handler= self.Handler,
                args= dict(val= 123))
        
        TESTS.AssertEqual(self.total, 123)
        
        dir = LOG.PARALLEL().SetMethodDone()

        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_THREAD_TESTS_2.',
            fileNames= [
                'TestExecution', # the pool
                'TestExecution.Handler' # the thread
            ])
        

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        LOG.Print(cls.TestAll)

        cls().TestExecution()
        
        LOG.PARALLEL().SetClassDone()