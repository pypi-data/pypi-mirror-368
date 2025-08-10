from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST
from .TESTS import  TESTS


class PARALLEL_PROCESS_TESTS_L(PARALLEL_TEST):

    ICON = '🧪'
    

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''
        
        LOG.Print(cls.TestAll)
        
        #cls().TestProcessPool()

        LOG.PARALLEL().SetClassDone()