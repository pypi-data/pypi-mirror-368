from LOG import LOG
from TESTS import  TESTS
from UTILS import  UTILS


class UTILS_OS_TESTS:


    @classmethod
    def TestAllOS(cls):
        LOG.Print('@')

        cls.TestDirectory()

        
    @classmethod
    def TestDirectory(cls):
        LOG.Print('@')
        
        dir = LOG.GetLogDir()
        dir.AssertExists()
        TESTS.AssertEqual(
            dir.GetName(), '__dumps__')
        
        dir = dir.GetSubDir('UTILS_OS_TESTS')
        TESTS.AssertEqual(
            dir.GetName(), 'UTILS_OS_TESTS')
        
        # Test the home directory.
        dir = UTILS.OS().Directory('~')
        TESTS.AssertTrue(
            dir.GetPath().startswith('/'))
        dir.AssertExists()