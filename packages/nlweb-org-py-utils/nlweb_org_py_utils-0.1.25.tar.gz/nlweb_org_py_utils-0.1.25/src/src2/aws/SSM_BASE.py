from LOG import LOG
from UTILS import UTILS
from LOG import LOG


class SSM_BASE:

    
    @classmethod
    def Set(cls, name: str, value: str):
        '''👉 Sets the parameter.'''
        pass # Abastract method.

    
    @classmethod
    def Get(cls, 
        name:str, 
        optional:bool= False,
        region:str= None
    ) -> str:
        '''👉 Gets the parameter.'''
        pass # Abastract method.


    @classmethod
    def SetOnceOnly(cls, name: str, value: str, region:str= None):
        '''🔒 Sets the parameter only if it is not already set.'''

        # Check if the parameter is already set.
        if cls.Get(name, optional= True):
            return
        
        # Set the parameter.
        cls.Set(name, value)