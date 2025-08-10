from .LOG import LOG
from .PARALLEL import  PARALLEL
from .PARALLEL_PROCESS import PARALLEL_PROCESS
from .PARALLEL_PROCESS_POOL import PARALLEL_PROCESS_POOL
from .PARALLEL_TEST import PARALLEL_TEST
from .TESTS import  TESTS


class PARALLEL_PROCESS_TESTS_J(PARALLEL_TEST):

    ICON = '🧪'


    def IsThisFruitNice(self, fruit:str):
        LOG.Print(self.IsThisFruitNice, f'({fruit})')

        return f'Yes, {fruit} is nice.'


    def TestProcessPool(self):
        LOG.Print(self.TestProcessPool)

        with PARALLEL_PROCESS_POOL() as pool:

            # List of processes to assert later if are DONE.
            processes:list[PARALLEL_PROCESS] = []

            # Loop through the fruits (expected results).
            for fruit in ['orange', 'appleJ', 'banana']:

                # Start the process.
                p = pool.StartProcess(
                    name = fruit,
                    handler= self.IsThisFruitNice,
                    args= dict(
                        fruit= fruit
                    ))
                
                # Add to assert later if all are DONE.
                processes.append(p)

            # Get the results before the .Stop()
            results = pool.GetResults()

        # Assert all processes are DONE.
        for p in processes:
            TESTS.AssertTrue(p.HasJoined())  

        result_keys = list(results.keys())
        TESTS.AssertEqual(len(result_keys), 3)
        TESTS.AssertEqual(result_keys, ['orange', 'appleJ', 'banana'])

        result_values = [
            results[fruit] for 
            fruit in results
        ]
        
        TESTS.AssertEqual(
            result_values, [
                'Yes, orange is nice.',
                'Yes, appleJ is nice.',
                'Yes, banana is nice.'
            ])
        
        TESTS.AssertEqual(pool.GetLog().GetStatus(), 'DONE')
        TESTS.AssertEqual(pool.GetLog().GetIconName(), 'DONE')  

        LOG.PARALLEL().SetMethodDone()
            

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''
        
        LOG.Print(cls.TestAll)
        
        cls().TestProcessPool()

        LOG.PARALLEL().SetClassDone()