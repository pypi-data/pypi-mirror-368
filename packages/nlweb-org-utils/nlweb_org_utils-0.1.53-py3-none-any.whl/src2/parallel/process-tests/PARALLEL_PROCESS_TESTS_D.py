
from LOG import LOG
from PARALLEL import  PARALLEL
from PARALLEL_TEST import PARALLEL_TEST


class PARALLEL_PROCESS_TESTS_D(PARALLEL_TEST):

    ICON = '🧪'


    def _TestLogHelper(self):
        from LOG import LOG

        LOG.Print('Just testing a process...')
        
        self.SaveBuffers()
        
        return 123


    def TestLog(self):
        LOG.Print(self.TestLog)
         
        with PARALLEL.PROCESS_POOL() as pool:
            process = pool.StartProcess(self._TestLogHelper)
            process.Join()

        self.LoadBuffers()
        self.AssertBufferCount(1)
        self.AssertBufferInfo(
            endsWith= f'{self._TestLogHelper.__name__}.md')

        dir = LOG.PARALLEL().SetMethodDone()

        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_PROCESS_TESTS_D.',
            fileNames= [
                'TestLog',
                'TestLog._TestLogHelper'
            ])

        # For processes, only the process log contains the prints.
        # This is because the process has a separate memory space.
        self.AssertLineInLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_PROCESS_TESTS_D.',
            fileNames= ['TestLog._TestLogHelper'],
            containsLine= 'Just testing a process...')
        

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''

        LOG.Print(cls.TestAll)
        
        cls().TestLog()

        LOG.PARALLEL().SetClassDone()