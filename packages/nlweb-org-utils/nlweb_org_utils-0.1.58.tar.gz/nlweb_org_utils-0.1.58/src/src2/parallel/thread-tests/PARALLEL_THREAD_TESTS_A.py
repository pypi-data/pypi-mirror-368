from LOG import LOG
from PARALLEL import  PARALLEL
from PARALLEL_TEST import PARALLEL_TEST
from STRUCT import  STRUCT
from TESTS import  TESTS
from UTILS import  UTILS


class PARALLEL_THREAD_TESTS_A(PARALLEL_TEST):

    ICON = '🧪'


    def Handler(self, id:str, items:list):
        if self.maxWorkers > 1:
            UTILS.Sleep(0.01)
        items.append(id)
        return f'*{id}*'


    def TestSimpleExecution(self, 
        maxWorkers:int, 
        collapse:bool=False
    ):
        
        # Print on a task.
        items = []
        self.maxWorkers = maxWorkers

        # Run the tasks, knowing that they will take 2 seconds to complete.
        pool = PARALLEL.THREAD_POOL(
            seconds= 5,
            maxWorkers= maxWorkers)
        
        # Ensure all logs have a different name.
        taskIDs = ['Task1', 'Task2', 'Task3']
        for i in range(len(taskIDs)):
            taskIDs[i] = f'{taskIDs[i]}({maxWorkers})'

        # Add the tasks to the runner.
        for name in taskIDs:
            pool.AddThread(
                name= name, 
                handler= self.Handler, 
                args= dict(
                    id= name, 
                    items= items))
        
        # Run the tasks.
        ret = pool.RunAllThreads()

        # Check if all tasks were considered.
        TESTS.AssertEqual(
            UTILS.SortList(items),
            taskIDs)
        
        # Check if all tasks have the correct results.
        for item in items:
            result = STRUCT(ret).RequireAtt(item)
            TESTS.AssertEqual(result, '*'+item+'*')

        # Check if the runner has no exceptions.
        pool.RaiseExceptions()

        if not collapse:
            # Clean up the log files.
            pool.DeleteLogFiles(reason='TestSimpleExecution loop')
            return

        dir = LOG.PARALLEL().SetMethodDone()
        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_THREAD_TESTS_A.',
            fileNames= [
                'TestSimpleExecution',

                'TestSimpleExecution.Task1(1)',
                'TestSimpleExecution.Task2(1)',
                'TestSimpleExecution.Task3(1)',

                'TestSimpleExecution.Task1(2)',
                'TestSimpleExecution.Task2(2)',
                'TestSimpleExecution.Task3(2)',

                'TestSimpleExecution.Task1(10)',
                'TestSimpleExecution.Task2(10)',
                'TestSimpleExecution.Task3(10)',
            ])


    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        LOG.Print(cls.TestAll)

        cls().TestSimpleExecution(maxWorkers= 1)
        cls().TestSimpleExecution(maxWorkers= 2)
        cls().TestSimpleExecution(maxWorkers= 10, collapse=True)

        LOG.PARALLEL().SetClassDone()