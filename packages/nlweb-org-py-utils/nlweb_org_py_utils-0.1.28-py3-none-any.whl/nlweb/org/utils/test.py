from LOG import LOG
print (LOG.hello())

from TEST_UTILS import TEST_UTILS
from RUNNER import RUNNER

RUNNER.RunFromConsole(
    file= __file__,
    name= __name__, 
    testFast= False,
    method= TEST_UTILS.TestUtils)