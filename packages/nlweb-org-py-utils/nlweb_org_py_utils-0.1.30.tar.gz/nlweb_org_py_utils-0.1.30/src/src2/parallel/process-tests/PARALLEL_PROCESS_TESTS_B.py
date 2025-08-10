from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST


class PARALLEL_PROCESS_TESTS_B(PARALLEL_TEST):

    ICON = '🧪'


    @classmethod
    def _ThreadHelper_TestProcessWithThread(cls):
        LOG.Print(cls._ThreadHelper_TestProcessWithThread, f': Inside the inner thread function.')
        LOG.RaiseException('@: Error in inner thread')

    @classmethod
    def ProcessHelper_TestProcessWithThread(cls):
        LOG.Print(cls.ProcessHelper_TestProcessWithThread, f': Inside the process helper.')
        PARALLEL.THREAD_POOL().RunThread(
            cls._ThreadHelper_TestProcessWithThread)

    @classmethod
    def TestProcessWithThread(cls):
        try:
            PARALLEL.PROCESS_POOL().RunProcess(
                cls.ProcessHelper_TestProcessWithThread)
        except Exception as e:
            if 'Error in inner thread' not in str(e):
                raise
        
        LOG.PARALLEL().SetMethodDone(
            method= cls.ProcessHelper_TestProcessWithThread)
        LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel with threads.'''

        LOG.Print(cls.TestAll)
        
        cls.TestProcessWithThread()

        LOG.PARALLEL().SetClassDone()