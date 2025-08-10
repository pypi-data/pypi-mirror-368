
from .STRUCT import STRUCT

import json
import boto3
events = boto3.client('events')

class EVENTBRIDGE_REAL_BUS(STRUCT):


    def __init__(self, name:str) -> None:
        super().__init__({
            'Name': name,
        })


    def Name(self):
        '''👉️ Returns the name of the bus.'''
        return self['Name']


    def Exists(self):
        '''👉️ Checks if the bus exists.'''
        try:
            events.describe_event_bus(Name= self.Name())
            return True
        except events.exceptions.ResourceNotFoundException:
            return False
    
   

    def Create(self):
        '''👉️ Creates a bus.'''
        return events.create_event_bus(Name= self.Name())
    

    def EnsureExists(self):
        '''👉️ Ensures that the bus exists.'''
        if not self.Exists():
            self.Create()