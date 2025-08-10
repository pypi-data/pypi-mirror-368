
from LOG import LOG
from PARALLEL import  PARALLEL
from PARALLEL_TEST import PARALLEL_TEST
from TESTS import  TESTS


class PARALLEL_PROCESS_TESTS_F(PARALLEL_TEST):

    ICON = '🧪'


    def _TestDirStructureHelper(self):
        from LOG import LOG

        LOG.Print('Just testing a process...')
        
        return 123


    def TestDirStructure(self):
        LOG.Print(self.TestDirStructure)
        
        name = 'box'
        
        pool = PARALLEL.PROCESS_POOL(
            name= name)

        ret = pool.RunProcess(
            handler= self._TestDirStructureHelper)
        
        TESTS.AssertEqual(ret, 123)
        TESTS.AssertEqual(pool.GetLog().GetStatus(), 'DONE')
        
        LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''

        LOG.Print(cls.TestAll)
        
        cls().TestDirStructure()

        LOG.PARALLEL().SetClassDone()