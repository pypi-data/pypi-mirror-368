from LOG import LOG
from PARALLEL import  PARALLEL
from PARALLEL_TEST import PARALLEL_TEST
from TESTS import  TESTS


class PARALLEL_THREAD_TESTS_1(PARALLEL_TEST):

    ICON = '🧪'


    def Handler(self, val:int):
        LOG.Print('Inside Handler')
        self.total += val
        return 999
    

    def TestExecution(self):
        
        self.total = 0

        pool = PARALLEL.THREAD_POOL()

        # Without with: the threads are not automatically executed.
        pool.AddThread(
            handler= self.Handler, 
            args= dict(val= 123))
        TESTS.AssertEqual(self.total, 0)

        # We need to run the threads manually.
        ret = pool.RunAllThreads()
        TESTS.AssertEqual(self.total, 123)
        
        # Check if the return value is correct.
        TESTS.AssertEqual(len(ret.Keys()), 1)
        TESTS.AssertEqual(ret.RequireAtt('Handler'), 999)
        
        dir = LOG.PARALLEL().SetMethodDone()

        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_THREAD_TESTS_1.',
            fileNames= [
                'TestExecution', # the pool
                'TestExecution.Handler' # the thread
            ],
            containsLines= [
                'Inside Handler'
            ])
        

    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        LOG.Print(cls.TestAll)

        cls().TestExecution()
        
        LOG.PARALLEL().SetClassDone()