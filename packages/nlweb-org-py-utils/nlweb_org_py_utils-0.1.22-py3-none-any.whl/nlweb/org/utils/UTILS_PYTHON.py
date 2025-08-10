from __future__ import annotations
import inspect
from types import CodeType

from DIRECTORY import DIRECTORY


class UTILS_PYTHON:


    @classmethod
    def CLASS(cls, class_:str|type):
        '''👉️ Returns the class object.'''
        from PYTHON_CLASS import PYTHON_CLASS
        return PYTHON_CLASS(class_)


    @classmethod
    def METHOD(cls, method:CodeType|callable):
        '''👉️ Returns the method object.'''
        from PYTHON_METHOD import  PYTHON_METHOD
        return PYTHON_METHOD(method)


    @classmethod
    def GetParentFunctionInfo(cls, goUp:int=0):
        '''👉️ Returns the parent function info.'''
        
        frame = cls._GetCallerFrame(goUp= goUp+1)
        code = frame.f_code
        qualname = code.co_qualname

        _split = qualname.split('.')
        class_name = _split[0]
        
        islocal = False
        parent_name = None
        if len(_split) > 1:
            islocal = _split[-2] == '<locals>'
            parent_name = _split[1]
        
        return dict(
            callable_is_inner= islocal,
            callable_parent_method_name= parent_name,
            callable_method_name= code.co_name,
            qualname = code.co_qualname,
            class_name = class_name)
            

    @classmethod
    def GetParentFunctionName(cls, goUp:int=0):
        '''👉️ Returns the name of the parent function.'''

        info = cls.GetParentFunctionInfo(goUp= goUp+1)
        if info['callable_is_inner']:
            return info['callable_parent_method_name']
        else:
            return info['callable_method_name']


    @classmethod
    def GetCaller(cls, goUp:int=0):
        '''👉️ Returns the caller.'''
        frame = cls._GetCallerFrame(goUp= goUp+1)
        from PYTHON_METHOD import  PYTHON_METHOD
        return PYTHON_METHOD(frame.f_code, frame.__class__)


    @classmethod
    def GetCallerFullName(cls, goUp:int=0):
        '''👉️ Returns the {module}.{name} of the caller.'''
        module_name = cls.GetCallerClassName(goUp= goUp+1)
        #caller_name = cls.GetCallerName(goUp= goUp+1)
        caller_name = cls.GetParentFunctionName(goUp= goUp+1)
        if caller_name == '<module>':
            return f'{module_name}'
        else:    
            return f'{module_name}.{caller_name}'


    @classmethod
    def _GetCallerFrame(cls, goUp:int=0):
        '''👉️ Returns the frame of the caller.'''
        frame = inspect.currentframe().f_back

        # Go up a few frames
        for i in range(goUp):
            frame = frame.f_back

        return frame


    @classmethod
    def GetCallerName(cls, goUp:int=0):
        '''👉️ Returns the name of the caller.'''
        from UTILS import  UTILS
        frame = cls._GetCallerFrame(goUp= goUp+1)
        ret = frame.f_code.co_name
        if ret == 'handler':
            raise Exception(frame.f_code)
        return ret


    @classmethod
    def GetCallerClassName(cls, goUp:int=0):
        '''👉️ Returns the name of the caller's module.'''
        info = cls.GetParentFunctionInfo(goUp= goUp+1)
        return info['class_name']
    

    @classmethod
    def GetMethod(cls, 
        className:str, 
        methodName:str
    ):
        # Get the class object from the class name
        clazz = globals()[className]

        # Get the method object
        method = getattr(clazz, methodName)

        from PYTHON_METHOD import  PYTHON_METHOD
        return PYTHON_METHOD(method)


    @classmethod
    def HellowWorldPython(cls, 
        dir:DIRECTORY= None
    ):
        from PYTHON_APP import PYTHON_APP
        app = PYTHON_APP(dir= dir)
        app.AddHellowWorldPython()
        return app
    

    @classmethod
    def HellowWorldStreamlit(cls, 
        dir:DIRECTORY= None
    ):
        from PYTHON_APP import PYTHON_APP
        app = PYTHON_APP(dir= dir)
        app.AddHellowWorldStreamlit()
        return app