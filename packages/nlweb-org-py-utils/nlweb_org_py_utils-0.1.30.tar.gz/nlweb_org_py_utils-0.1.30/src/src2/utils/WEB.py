# 📚 WEB

from .WEB_BASE import WEB_BASE
from .AWS import AWS

def WEB():

    if AWS.LAMBDA().IsLambda():
        from .WEB_REAL import WEB_REAL
        return WEB_REAL()
    
    else:
        from .WEB_MOCK import  WEB_MOCK
        return WEB_MOCK()