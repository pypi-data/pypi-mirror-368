from LOG import LOG
from PARALLEL_THREAD import  PARALLEL_THREAD
from UTILS import  UTILS


class PARALLEL_THREAD_WRAPPER:

    ICON = '🏎️'

    
    @classmethod
    def Wrap(cls, thread:PARALLEL_THREAD, pool):
        '''👉️ Runs a task and updates the display.'''
        
        from PARALLEL_THREAD_POOL import  PARALLEL_THREAD_POOL
        UTILS.AssertIsType(pool, PARALLEL_THREAD_POOL, require=True)
        runner: PARALLEL_THREAD_POOL = pool
        
        name = thread.GetName()
        log = LOG.PARALLEL().LogThread(
            name= name, 
            path= thread._logPath)

        try:           
            thread.SetStarted()
            log.SetRunning()

            ret = cls._Run(task=thread, pool= runner)

            thread.SetDone(ret)
            log.SetDone()

            LOG.Print(cls.Wrap, f'[{name}]: done, returning:', ret)
            return {
                'Task': name,
                'Result': ret
            }
            
        except Exception as e:
            thread.SetFailed(e)
            log.SetFail(e)
            
            return {
                'Task': name,
                'Result': None,
                'ExceptionMessage': str(e),
                'ExceptionType': type(e).__name__
            }

        finally:
            log.Stop()


    @classmethod
    def _Run(cls, task:PARALLEL_THREAD, pool):
        '''👉️ Runs the task with the args.'''
        LOG.Print(cls._Run, f'[{task.GetName()}]', task)
        
        from PARALLEL_THREAD_POOL import  PARALLEL_THREAD_POOL
        UTILS.AssertIsType(pool, PARALLEL_THREAD_POOL, require=True)
        runner: PARALLEL_THREAD_POOL = pool

        if not task.Continue():
            LOG.RaiseException('You should not have called me!')

        if not task.Continue():
            LOG.Print(cls._Run, f'[{task.GetName()}]: not ready to continue')
            return None
        
        if not runner.ContinueRun():
            LOG.Print(cls._Run, f': The pool told us to stop.')
            return None
        
        LOG.Print(cls._Run, f'[{task.GetName}]: calling')

        if isinstance(task._args, dict):
            task._args['runner'] = runner
        elif isinstance(task._args, list):
            task._args.append(runner)
            LOG.RaiseException('A LIST, REALLY?')
        elif task._args == None:
            task._args = {'runner': runner}

        from PYTHON_METHOD import  PYTHON_METHOD
        task._result = PYTHON_METHOD(
            task._task
        ).InvokeWithMatchingArgs(
            args= task._args,
            optional= ['runner'])

        LOG.Print(cls._Run, f'[{task._name}]: success', 
            'result=', task._result, 
            task)
        
        return task._result