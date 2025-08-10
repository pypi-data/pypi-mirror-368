
from LOG import LOG
from PARALLEL import  PARALLEL
from PARALLEL_TEST import PARALLEL_TEST
from STRUCT import  STRUCT
from TESTS import  TESTS
from UTILS import  UTILS


class PARALLEL_THREAD_TESTS_B(PARALLEL_TEST):

    ICON = '🧪'


    def TestAddingTasksMidway(self, 
        maxWorkers:int, 
        timeout:int= 5,
        pause:float= 0.5,
        collapse:bool=False
    ):
        def map(name:str):
            return f'{name}({maxWorkers})'

        items = []
        def handler(id:str, items:list):

            if id == map('SubTask1'):
                
                # While the previous are running, add more tasks using .AddTask().
                for childName in [
                    map('SubTask4'), 
                    map('SubTask5')
                ]:
                    pool.AddThread(
                        name= childName, 
                        handler= handler, 
                        args= dict(
                            id= childName, 
                            items= items), 
                        ensureSubRunner= True)

            if id == map('SubTask2'):
                # While the previous are running, add more tasks using .RunTaskList().
                
                def SubTask6(): 
                    return handler(
                        id=map('SubTask6'), 
                        items=items)
                
                def SubTask7(): 
                    return handler(
                        id=map('SubTask7'), 
                        items=items)
                
                pool.RunThreadList(
                    handlers= [SubTask6, SubTask7], 
                    names= [map('SubTask6'), map('SubTask7')],
                    ensureSubRunner=True)

            if maxWorkers > 1:
                UTILS.Sleep(pause)
            
            if id in items:
                LOG.RaiseException(f'🔴 Task {id} was already run!')

            items.append(id)
            return f'*{id}*'

        # Run the tasks, knowing that they will take 2 seconds to complete.
        pool = PARALLEL.THREAD_POOL(
            maxWorkers= maxWorkers,
            name= f'Pool({maxWorkers})',
            seconds= timeout)
        
        for name in [
            map('SubTask1'), 
            map('SubTask2'), 
            map('SubTask3')
        ]:
            pool.AddThread(
                name= name, 
                handler= handler, 
                args= dict(id=name, items=items))

        ret = pool.RunAllThreads()

        # Check if all tasks were considered.
        TESTS.AssertEqual(
            UTILS.SortList(items),
            [
                map('SubTask1'), 
                map('SubTask2'), 
                map('SubTask3'), 
                map('SubTask4'), 
                map('SubTask5'), 
                map('SubTask6'), 
                map('SubTask7')
            ])
        
        # Check if all tasks have the correct results.
        for item in UTILS.SortList(items):
            result = STRUCT(ret).RequireAtt(item)
            UTILS.AssertEqual(
                given= result, 
                expect= '*'+item+'*', 
                msg=f'Did task [{item}] run?')
            
        if not collapse:
            return
        
        dir = LOG.PARALLEL().SetMethodDone()
        self.AssertDirLogFiles(
            dir= dir,
            prefix= '🟢 PARALLEL_THREAD_TESTS_B.',
            fileNames= [
                'TestAddingTasksMidway.Pool(1)',
                'TestAddingTasksMidway.Pool(10)',
                'TestAddingTasksMidway.Pool(2)',
                'TestAddingTasksMidway.SubTask1(1)',
                'TestAddingTasksMidway.SubTask1(10)',
                'TestAddingTasksMidway.SubTask1(2)',
                'TestAddingTasksMidway.SubTask2(1)',
                'TestAddingTasksMidway.SubTask2(10)',
                'TestAddingTasksMidway.SubTask2(2)',
                'TestAddingTasksMidway.SubTask3(1)',
                'TestAddingTasksMidway.SubTask3(10)',
                'TestAddingTasksMidway.SubTask3(2)',
                'TestAddingTasksMidway.SubTask4(1)',
                'TestAddingTasksMidway.SubTask4(10)',
                'TestAddingTasksMidway.SubTask4(2)',
                'TestAddingTasksMidway.SubTask5(1)',
                'TestAddingTasksMidway.SubTask5(10)',
                'TestAddingTasksMidway.SubTask5(2)',
                'TestAddingTasksMidway.SubTask6(1)',
                'TestAddingTasksMidway.SubTask6(10)',
                'TestAddingTasksMidway.SubTask6(2)'
            ])

        
    @classmethod
    def TestAll(cls):
        '''👉️ Test the parallel thread.'''

        LOG.Print(cls.TestAll)

        cls().TestAddingTasksMidway(maxWorkers= 1, timeout=6, pause=0.05)
        cls().TestAddingTasksMidway(maxWorkers= 2, timeout=3, pause=0.1)
        cls().TestAddingTasksMidway(maxWorkers= 10, timeout=3, pause=0.5, collapse=True)

        LOG.PARALLEL().SetClassDone()