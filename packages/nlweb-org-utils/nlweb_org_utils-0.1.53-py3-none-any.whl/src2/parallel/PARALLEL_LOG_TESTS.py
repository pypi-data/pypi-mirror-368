from LOG_BUFFER import LOG_BUFFER
from STRUCT import  STRUCT
from TESTS import  TESTS
from UTILS import  UTILS
from LOG import LOG
from PARALLEL import  PARALLEL


class PARALLEL_LOG_TESTS:

    ICON = '🧪'


    @classmethod
    def thread_function(cls, 
        name:str, 
        results:dict, 
        fn:callable, 
        kargs:dict
    ):
        
        try:
            from PYTHON_METHOD import  PYTHON_METHOD
            PYTHON_METHOD(fn).InvokeWithMatchingArgs(kargs)

            results[name] = {
                'Status': 'Done',
            }
        except Exception as e:
            results[name] = {
                'Status': 'Exception',
                'Exception': e,
            }

    
    @classmethod
    def _CommonRunTask(cls, 
        name:str, 
        fn:callable, 
        kargs:dict
    ):

        import threading
        results:dict = {}

        thread = threading.Thread(
            name= name,
            target= cls.thread_function, 
            args= (name, results, fn, kargs))
        
        thread.start()
        thread.join()  # Wait for the thread to complete
        
        if STRUCT(results).RequireStruct(name).RequireStr('Status') == 'Exception':
            raise results[name]['Exception']


    @classmethod
    def TestParallelLog(cls):
        LOG.Print('🧪‍ PARALLEL_LOG_TESTS.TestParallelLog()')

        buffers:dict[str,LOG_BUFFER] = {}

        # Print on an unkown thread.
        LOG.Print('Unkown running') 
        
        # Print on the main thread.
        with LOG.LogProcess(
            name='TestParallelLog') as processBuffer:

            buffers[cls.TestParallelLog.__name__] = processBuffer

            LOG.Print('Main running')

            # Print on a task.
            def _MyThreadFunction(
                name:str, 
                success:bool=None, 
                threadBuffer:LOG_BUFFER=None
            ):
                LOG.LogThread(threadBuffer)
                LOG.Print(f'{name} running')
                
                if success == True: 
                    threadBuffer.SetDone()
                elif success == False:
                    threadBuffer.SetFail('Task failed')
                else:
                    pass


            def _MyRunTask(name:str, success:bool=None):
                with LOG.CreateBuffer(name) as threadBuffer:
                    buffers[name] = threadBuffer

                    # Execute the task.
                    cls._CommonRunTask(
                        name= name, 
                        fn= _MyThreadFunction, 
                        kargs=dict(
                            name= name, 
                            success= success, 
                            threadBuffer= threadBuffer))

                    # Assert the registered threads.
                    if not LOG.Settings().GetTestFast():
                        TESTS.AssertNotEqual(
                            threadBuffer.GetLogs(), [])
                        UTILS.AssertContains(
                            lst= threadBuffer.GetLogs(), 
                            value= f'{name} running')

            _MyRunTask('TaskRunning')
            _MyRunTask('TaskSuccessed', True)
            _MyRunTask('TaskFailed', False)

            # Stop parallel logging.
        LOG.Print('Unkown stopped') 

        # Dump the logs.
        buffers[cls.TestParallelLog.__name__].DumpToFile()
        main = LOG.Buffer()

        # Assert the main location.
        main.GetDir().AssertName('__dumps__')

        # Read the main content.
        main.DumpToFile()
        if not LOG.Settings().GetTestFast():
            lines = main.ReadLogLines()
            if lines == []:
                LOG.RaiseException(
                    f'Empty log file,'
                    f' - did you forget to Dump the file?', main)
        
        # Check the main log content.
        if not LOG.Settings().GetTestFast():
            TESTS.AssertTrue(
                UTILS.ContainsAll(
                    lines, [ 
                        'Unkown running',
                        'Main running'  ,
                        'TaskRunning running',
                        'TaskSuccessed running',
                        'TaskFailed running',
                        'Unkown stopped'
                    ]))
        
        # Get a main task
        processLog = buffers[cls.TestParallelLog.__name__]
        
        # Assert the main task location.
        processLog.GetDir().AssertName('PARALLEL')
        nameBeforeUuid = processLog.GetNameWithoutIcon().split('[')[0]
        TESTS.AssertEqual(nameBeforeUuid, 
                f'{PARALLEL_LOG_TESTS.__name__}.'
                f'{cls.TestParallelLog.__name__}.'
                f'{cls.TestParallelLog.__name__}.md')
        TESTS.AssertFalse(
            processLog.GetName().endswith('].md'))
        
        if not LOG.Settings().GetTestFast():
            TESTS.AssertTrue(
                UTILS.ContainsAll(
                    processLog.ReadLogLines(), [
                        'Main running'
                    ]))

        # Get a sub task
        successTaskLog = buffers['TaskSuccessed']      
        nameBeforeUuid = successTaskLog.GetNameWithoutIcon().split('[')[0]  
        TESTS.AssertEqual(nameBeforeUuid,
            f'{PARALLEL_LOG_TESTS.__name__}.'
            f'{PARALLEL_LOG_TESTS.TestParallelLog.__name__}.'
            f'TaskSuccessed.md')

        # Assert the failed task.
        failedTaskLog = buffers['TaskFailed']
        failedTaskLog.GetDir().AssertName('PARALLEL')

        # Check the failed task log content.
        if not LOG.Settings().GetTestFast():
            logs = failedTaskLog.ReadLogLines()
            TESTS.AssertEqual(logs[0], 'TaskFailed running')

        taskRunningLog = buffers['TaskRunning']
        if not LOG.Settings().GetTestFast():
            UTILS.AssertContains(
                lst= taskRunningLog.ReadLogLines(), 
                value= 'TaskRunning running')
        
        taskSuccessedLog = buffers['TaskSuccessed']
        if not LOG.Settings().GetTestFast():
            UTILS.AssertContains(
                lst= taskSuccessedLog.ReadLogLines(), 
                value= 'TaskSuccessed running')
        
        # Delete the logs.
        for buffer in buffers.values():
            buffer.Delete(reason='TestParallelLog()')
            pass
        