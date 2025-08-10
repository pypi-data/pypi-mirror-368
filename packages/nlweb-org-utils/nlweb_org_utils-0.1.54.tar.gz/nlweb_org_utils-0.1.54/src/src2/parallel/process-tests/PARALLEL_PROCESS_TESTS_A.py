from LOG import LOG
from PARALLEL import  PARALLEL
from PARALLEL_TEST import PARALLEL_TEST
from TESTS import  TESTS


class PARALLEL_PROCESS_TESTS_A(PARALLEL_TEST):

    ICON = '🧪'


    def IsThisFruitNice(self, fruit:str):
        try:
            LOG.Print(self.IsThisFruitNice, f'({fruit})')
            LOG.Print(f'Inside IsThisFruitNice.')

            return f'Yes, {fruit} is nice.' 
        
        except Exception as e:
            LOG.Print(self.IsThisFruitNice, f'({fruit}): exception', e)
            return f'No, {fruit} is not nice. Exception: {str(e)}'


    def TestProcessStatus(self):
        LOG.Print(self.TestProcessStatus)

        with PARALLEL.PROCESS_POOL() as pool:

            p = pool.StartProcess(
                handler= self.IsThisFruitNice,
                args= dict(
                    fruit= 'appleA'),
                )

            result = p.GetResult()
            TESTS.AssertEqual(result, 'Yes, appleA is nice.')
        
        TESTS.AssertEqual(pool.GetLog().GetStatus(), 'DONE')
        TESTS.AssertEqual(pool.GetLog().GetIconName(), 'DONE')

        dir = LOG.PARALLEL().SetMethodDone()
        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_PROCESS_TESTS_A.',
            fileNames= [
                'TestProcessStatus',
                'TestProcessStatus.IsThisFruitNice'
            ],
            containsText= [
                'Yes, appleA is nice.'
            ])

        # For processes, only the process log contains the prints.
        # This is because the process has a separate memory space.
        self.AssertLineInLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_PROCESS_TESTS_A.',
            fileNames= ['TestProcessStatus.IsThisFruitNice'],
            containsLine= 'Inside IsThisFruitNice.')


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''

        LOG.Print(cls.TestAll)
        
        cls().TestProcessStatus()
        
        LOG.PARALLEL().SetClassDone()