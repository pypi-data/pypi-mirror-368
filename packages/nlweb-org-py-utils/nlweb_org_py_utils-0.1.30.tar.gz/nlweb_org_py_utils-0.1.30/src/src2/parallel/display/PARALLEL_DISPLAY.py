
import threading

from .LOG import LOG
from .PARALLEL_DISPLAY_SLOT import PARALLEL_DISPLAY_SLOT


class PARALLEL_DISPLAY():

    # Lock for the display
    lock = threading.Lock()

    def __init__(self, threads:int):

        # Create a list of slots
        self._slots:list[PARALLEL_DISPLAY_SLOT] = []
        for i in range(threads):
            slot = PARALLEL_DISPLAY_SLOT(i+1)
            self._slots.append(slot)

        self.ClearScreen()


    def ClearScreen(self):
        '''👉️ Clears the screen.'''
        
        import os
        os.system('cls' if os.name == 'nt' else 'clear')


    def StartSlot(self, description:str):
        '''👉️ Starts a slot and returns it.'''

        with PARALLEL_DISPLAY.lock:

            # get a list of all free slots
            freeSlots:list[PARALLEL_DISPLAY_SLOT] = []
            for slot in self._slots:
                if slot.IsFree():
                    freeSlots.append(slot)
            if len(freeSlots) == 0:
                LOG.RaiseException('No free slots available!')
            
            # get the free slot with the lowest sequence
            freeSlots.sort(key=lambda x: x.GetSequence())
            selected = freeSlots[0]

            # return the selected slot
            selected.Start(description=description)
            return selected        


    def RaiseExceptions(self):
        '''👉️ Raises all exceptions in the slots.'''
        for slot in self._slots:
            slot.RaiseException()


    def NoFailuresSoFar(self):
        '''👉️ Returns True if no failures so far.'''
        for slot in self._slots:
            if slot.IsFailed():
                return False
        return True