from .LOG import LOG
from .UTILS import UTILS


class LAMBDA_FUNCTION():
    '''👉 Base class for Lambda functions.'''

    ICON = '🦙'


    def __init__(self, 
        cached: bool= False):
        '''👉 Initialize the class.'''

        self._cached = cached
        if cached: self._cache = UTILS.CACHE()

        self.Name = ''


    def GetArn(self):
        LOG.RaiseException('Overide!')