
from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST
from .TESTS import  TESTS


class PARALLEL_THREAD_TESTS_G(PARALLEL_TEST):

    ICON = '🧪'


    def Helper(self):
        return 1/0


    def TestFailureRunTaskListWith(self):

        # Expect a division by zero error.
        with TESTS.AssertValidation(type= ZeroDivisionError):
            with PARALLEL.THREAD_POOL() as pool:
                pool.RunThreadList([
                    self.Helper
                ])

        # Verify the status.
        TESTS.AssertEqual(pool.GetLog().GetStatus(), 'FAILED')
        TESTS.AssertEqual(pool.GetLog().GetIconName(), 'FAILED')
        TESTS.AssertEqual(pool.GetLog().GetNameWithoutIcon(), 
            f'{PARALLEL_THREAD_TESTS_G.__name__}.'
            f'{PARALLEL_THREAD_TESTS_G.TestFailureRunTaskListWith.__name__}.md')
        
        dir = LOG.PARALLEL().SetMethodDone()

        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🔴 PARALLEL_THREAD_TESTS_G.',
            fileNames= [
                'TestFailureRunTaskListWith',
                'TestFailureRunTaskListWith.Helper'
            ],
            containsText= [
                'ZeroDivisionError'
            ])


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        LOG.Print(cls.TestAll)
        
        cls().TestFailureRunTaskListWith()
        
        LOG.PARALLEL().SetClassDone()
