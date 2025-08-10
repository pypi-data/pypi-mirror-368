from DIRECTORY import  DIRECTORY
from FILESYSTEM_OBJECT import  FILESYSTEM_OBJECT
from LOG_BUFFER import LOG_BUFFER
from LOG_BUFFER_INFO import LOG_BUFFER_INFO
from STRUCT import  STRUCT
from TESTS import  TESTS
from UTILS import  UTILS
from LOG import LOG

class PARALLEL_TEST:


    def __init__(self):
        '''👉️ Initialize the test.'''
        self._name = f'🧠 {self.__class__.__name__}.yaml'
        
        from LOG import LOG
        self._file = LOG.GetParallelLogDir().GetFile(self._name)


    def __exit__(self, exc_type, exc_value, traceback):
        self._file.Delete()


    def Save(self, **kwargs):
        self._file.WriteYaml(kwargs)
        

    def Load(self):
        return self._file.ReadYaml()
    

    def SaveBuffers(self, buffers:list[LOG_BUFFER]=None):
        '''👉️ Save the buffers.'''
        if not buffers:
            from LOG import LOG
            buffers = LOG.PARALLEL().GetCurrentBuffers()
        infos = [
            buffer.GetInfo() 
            for buffer in buffers
        ]
        self.Save(Buffers= infos)

    
    def LoadBuffers(self):
        '''👉️ Load the buffers.'''
        saved = self.Load()['Buffers']
        buffers:list[LOG_BUFFER_INFO] = []
        for info in saved:
            buffer = LOG_BUFFER_INFO(info)
            buffers.append(buffer)
        self._buffers = buffers


    def Assert(self, **kwargs):
        for key, value in kwargs.items():
            assert getattr(self, f'_{key}') == value, f'{key} should be {value}.'
    

    def AssertBufferCount(self, count:int):
        '''👉️ Assert the buffer count.'''
        UTILS.AssertEqual(
            len(self._buffers), count, 
            msg=f'Buffer count should be {count}.')


    def AssertBufferInfo(self, 
        index:int=0, 
        endsWith:str=None, 
        containsLine:str=None,
        **kwargs
    ):
        '''👉️ Assert the buffer info.'''

        buffer = self._buffers[index]
        if endsWith:
            TESTS.AssertTrue(
                buffer.FileNameWithoutIcon.endswith(endsWith), 
                msg=f'FileNameWithoutIcon [{buffer.FileNameWithoutIcon}] should end with [{endsWith}].')
            
        for key, value in kwargs.items():
            UTILS.AssertEqual(
                getattr(buffer, key), value, 
                msg=f'{key} should be {value}.')

        if containsLine:
            from FILESYSTEM import  FILESYSTEM
            file = FILESYSTEM.FILE(buffer.Path)
            lines = file.ReadLogLines()
            assert containsLine in lines, f'7# Line should contain {containsLine}.'


    def AssertDirLogFiles(self, 
        fileNames:list[str],
        dir:DIRECTORY= None, 
        files:dict[str, FILESYSTEM_OBJECT]= None,
        prefix:str= '',
        containsLines:list[str]=None,
        containsText:list[str]=None,
    ):
        '''👉️ Assert the files exist.'''
           
        # Verify the logs exist.
        for name in fileNames:
            find = f'{prefix}{name}.md'
            if dir:
                file = dir.RequireFile(find)
            else:
                file = STRUCT(files).RequireAtt(find)

            # Verify the lines in the logs.
            if not LOG.Settings().GetTestFast():
                if containsLines:
                    lines = file.ReadLogLines()
                    for line in containsLines:
                        assert line in lines, f'9# Line should contain {line} in file {name}.'

            # Verify the text in the logs.
            if not LOG.Settings().GetTestFast():
                if containsText:
                    content = file.ReadText()
                    for text in containsText:
                        assert text in content, f'File content should contain {text} in file {name}.'
        

    def AssertLineInLogFiles(self, 
        dir:DIRECTORY, 
        fileNames:list[str], 
        prefix:str, 
        containsLine:str
    ):
        '''👉️ Assert the line in the log file.'''
        if not LOG.Settings().GetTestFast():
            for name in fileNames:
                file = dir.GetFile(f'{prefix}{name}.md')
                lines = file.ReadLogLines()
                assert containsLine in lines, f'4# Line should contain `{containsLine}` in file {name} (testFast={LOG.Settings().GetTestFast()}).' 