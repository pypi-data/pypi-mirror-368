from LOG import LOG
from PARALLEL import  PARALLEL
from PARALLEL_TEST import PARALLEL_TEST
from TESTS import  TESTS
from UTILS import  UTILS


class PARALLEL_PROCESS_TESTS_E(PARALLEL_TEST):

    ICON = '🧪'


    def _TestLogErrorHelper1(self):
        UTILS.Sleep(0.1)
        print(1/0)

    
    def _TestLogErrorHelper2(self):
        UTILS.Sleep(0.1)
        print(1/0)

    
    def TestLogError(self):
        LOG.Print(self.TestLogError)
         
        # Without join.
        with TESTS.AssertValidation(check='division by zero'):
            with PARALLEL.PROCESS_POOL() as pool:
                pool.StartProcess(self._TestLogErrorHelper1)
                pool.StartProcess(self._TestLogErrorHelper2)

        # With join.
        with TESTS.AssertValidation(check='division by zero'):
            with PARALLEL.PROCESS_POOL() as pool:
                pool.StartProcess(self._TestLogErrorHelper1).Join()
            
        LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel process.'''

        LOG.Print(cls.TestAll)
        
        cls().TestLogError()

        LOG.PARALLEL().SetClassDone()