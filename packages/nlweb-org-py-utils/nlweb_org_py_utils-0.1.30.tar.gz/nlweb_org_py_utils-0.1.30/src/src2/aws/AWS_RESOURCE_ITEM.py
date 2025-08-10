from .AWS_RETRY import RetryWithBackoff
from .LOG import LOG
from .PRINTABLE import PRINTABLE
from .UTILS import UTILS


from typing import TypeVar, Generic, List
from abc import ABC, abstractmethod

# Create a type variable that can be 'AWS_RESOURCE_ITEM' or any subclass of it
AWS_RESOURCE_ITEM_TYPE = TypeVar(
    'AWS_RESOURCE_ITEM_TYPE', 
    bound='AWS_RESOURCE_ITEM')


class AWS_RESOURCE_ITEM(ABC, PRINTABLE):
    '''👉️ Represents an AWS resource.
    
    Implement the following methods:
      * _Delete(self)
      
    '''

    ICON = '⛅'


    def __init__(self, 
        pool, 
        client,
        arn:str, 
        name:str,
        resource=None
    ) -> None:
        LOG.Print(f'@', f'{name=}', f'{arn=}')

        # Validate the pool.
        from .AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
        assert isinstance(pool, type)
        assert issubclass(pool, AWS_RESOURCE_POOL)
        self.Pool:AWS_RESOURCE_POOL = pool
        '''👉️ The pool of resources that manages the resource item.'''

        # Validate the client.
        UTILS.Require(client)
        self.Client = client
        '''👉️ The boto3 client to access the AWS API.'''

        # Validate the resource.
        self.Resource = resource
        '''👉️ The boto3 resource to access the AWS API.'''

        # Add the other properties.
        self.Arn = arn
        '''👉️ The ARN of the AWS resource.'''
        
        self.Name = name
        '''👉️ The name of the AWS resource.'''

        self.RetainOnFailure: bool= False
        '''👉️ If True, the resource will not be deleted on with.__exit__() if an exception occurs. 
        * Default: False

        Usage: 
            ```python
            with <create>() as r:
                r.RetainOnFailure = True
                ...
            ```
        '''

        self.Retain: bool= False
        '''👉️ If True, the resource will not be deleted on with.__exit__().
        * Default: False

        Usage:
            ```python
            with <create>() as r:
                r.Retain = True
                ...
            ```
        '''

        PRINTABLE.__init__(self, lambda: {
            'Arn': self.Arn,
            'Name': self.Name
        })


    @abstractmethod
    def _Delete(self):
        LOG.RaiseException('Implement.')


    @RetryWithBackoff(maxRetries=10, initialDelay=0.1)
    def Delete(self):
        '''👉️ Delete the resource.'''
        LOG.Print('@', self)
        self._Delete()
        self.WaitUntilDeleted()


    def __enter__(self):
        return self
    

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''👉️ Cleanup.'''
        LOG.Print('@', self)

        if exc_type:
            LOG.Print(f'@ Exception: {exc_val}')
            
            if self.RetainOnFailure:
                LOG.Print(f'@ Retaining resource on failure: {type(self).__name__}.')
                return False
                        
        if self.Retain:
            LOG.Print(f'@ Retaining resource: {type(self).__name__}.')
            return False

        self.Delete()


    def Exists(self):
        '''👉️ Returns True if the resource exists.'''
        return self.Pool.Exists(
            name= self.Name,
            client= self.Client)


    def AssertExists(self):
        '''👉️ Raise an exception if the resource does not exist.'''
        LOG.Print('@', self)
        if not self.Exists():
            LOG.RaiseValidationException(
                f'Resource [{self.Name}] should exist.')
    

    @RetryWithBackoff(maxRetries=8, initialDelay=0.1)
    def WaitUntilListed(self):
        '''👉️ Waits until the resource exists.'''
        LOG.Print('@', self)
        self.AssertExists()


    def AssertNotListed(self):
        '''👉️ Raise an exception if the resource exists.'''
        LOG.Print('@', self)
        if self.Exists():
            LOG.RaiseValidationException(
                f'Resource [{self.Name}] should not exist!')


    @RetryWithBackoff(maxRetries=10, initialDelay=0.1)
    def WaitUntilDeleted(self):
        '''👉️ Waits until the resource is deleted.'''
        LOG.Print('@', self)
        self.AssertNotListed()


