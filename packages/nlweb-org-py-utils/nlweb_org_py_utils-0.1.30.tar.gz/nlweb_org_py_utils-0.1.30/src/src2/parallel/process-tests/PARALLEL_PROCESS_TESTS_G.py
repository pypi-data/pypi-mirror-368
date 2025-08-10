
from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_TEST import PARALLEL_TEST
from .TESTS import  TESTS


class PARALLEL_PROCESS_TESTS_G(PARALLEL_TEST):

    ICON = '🧪'

    
    def IsThisFruitNice(self, fruit:str):
        LOG.Print(self.IsThisFruitNice, f'({fruit})')

        return f'Yes, {fruit} is nice.'

    
    def TestFruitAnswers(cls):
        LOG.Print(cls.TestFruitAnswers)

        pool = PARALLEL.PROCESS_POOL()

        TESTS.AssertEqual(
            pool.GetLog().GetNameWithoutIcon(),
            f'{PARALLEL_PROCESS_TESTS_G.__name__}.'
            f'{cls.TestFruitAnswers.__name__}.md')
        
        result = pool.RunProcess(
            handler= cls.IsThisFruitNice,
            args= dict(
                fruit= 'apple2'))
        
        TESTS.AssertEqual(result, 'Yes, apple2 is nice.')
        TESTS.AssertEqual(pool.GetLog().GetStatus(), 'DONE')
        TESTS.AssertEqual(pool.GetLog().GetIconName(), 'DONE')

        LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''
        
        LOG.Print(cls.TestAll)
        
        cls().TestFruitAnswers()

        LOG.PARALLEL().SetClassDone()