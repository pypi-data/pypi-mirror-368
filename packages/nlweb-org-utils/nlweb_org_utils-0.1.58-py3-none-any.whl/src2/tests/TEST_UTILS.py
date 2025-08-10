class TEST_UTILS:


    @classmethod
    def Run(cls):

        # -----------------------------
        # Log.
        # -----------------------------
        
        from LOG_TESTS import LOG_TESTS
        LOG_TESTS.TestAllLogs()

        # -----------------------------
        # Utils.
        # -----------------------------
        
        from TESTS_TESTS import  TESTS_TESTS
        TESTS_TESTS.TestAllTests()
        
        from UTILS_TESTS import UTILS_TESTS
        UTILS_TESTS.TestAllUtils()
        
        from WEB_TESTS import WEB_TESTS
        WEB_TESTS.TestAllWeb()
        
        from STRUCT_TESTS import STRUCT_TESTS
        STRUCT_TESTS.TestAllStruct()

        from FILESYSTEM_TESTS import FILESYSTEM_TESTS
        FILESYSTEM_TESTS.TestAllFileSystem()

        from FILE_TESTS import FILE_TESTS
        FILE_TESTS.TestAllFile()

        from DIRECTORY_TESTS import DIRECTORY_TESTS
        DIRECTORY_TESTS.TestAllDirectory()
 
        # -----------------------------
        # PARALLEL 
        # -----------------------------

        from PARALLEL_TESTS import PARALLEL_TESTS
        PARALLEL_TESTS.TestAllParallel()


    @classmethod
    def TestUtils(cls):

        from LOG import LOG
        from PARALLEL import  PARALLEL

        with PARALLEL.THREAD_POOL() as pool:
            pool.RunThread(cls.Run)

        LOG.PARALLEL().SetClassDone()


from RUNNER import RUNNER
RUNNER.RunFromConsole(
    file= __file__,
    name= __name__, 
    testFast= True,
    method= lambda: TEST_UTILS.TestUtils())