from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST


class PARALLEL_PROCESS_TESTS_C1(PARALLEL_TEST):

    ICON = '🧪'


    def _Thread(self):
        LOG.Print('Inside the thread..')
        

    def _Process(self, parallel:bool = False):
        with PARALLEL.THREAD_POOL() as pool:
            pool.RunThreadList([
                self._Thread
            ], parallel= parallel)


    def TestProcessWithThread(self, parallel:bool = False):
        with PARALLEL.PROCESS_POOL(
            seconds= 60 * 10) as pool:

            pool.StartProcess(
                handler= self._Process,
                args= dict(
                    parallel= parallel))
            
        dir = LOG.PARALLEL().SetClassDone()
        
        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_PROCESS_TESTS_C1.',
            fileNames= [
                '_Process._Thread',
                '_Process',
                'TestProcessWithThread._Process',
                'TestProcessWithThread'
            ])
        

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel with threads.'''

        LOG.Print(cls.TestAll)
        
        # Same as C2, but without error.
        cls().TestProcessWithThread(parallel= True)

        LOG.PARALLEL().SetClassDone()