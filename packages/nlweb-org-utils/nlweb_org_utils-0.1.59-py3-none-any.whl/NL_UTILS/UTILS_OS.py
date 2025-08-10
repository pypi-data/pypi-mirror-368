# 📚 UTILS

from __future__ import annotations
from .UTILS_YAML import UTILS_YAML
from .LOG import LOG
import os


class UTILS_OS(UTILS_YAML):
    '''👉️ Generic methods to work with the file system.'''
   

    @classmethod
    def IsLambda(cls):
        '''👉️ Returns true if the code is running on AWS Lambda.'''
        import os
        return 'AWS_EXECUTION_ENV' in os.environ
    

    @classmethod
    def RequireCommandLineScript(cls):
        '''👉️ Throws an exception if the code is not running as a command line script.'''
        if not cls.IsCommandLineScript():
            LOG.RaiseException('This script should be run as a command line script.')

    
    @classmethod
    def IsCommandLineScript(cls):
        '''👉️ Returns true if the code is running as a command line script.'''

        # Get the entire call stack
        import inspect
        stack = inspect.stack()

        # The first item in the call stack should be the original script
        first_frame = stack[-1]

        # Inspect the module name in the first frame
        module = inspect.getmodule(first_frame[0])
        ret = \
            module == None or \
            module.__name__ == "__main__"
        
        LOG.Print(' UTILS.OS.IsCommandLineScript: ' + str(ret))
        return ret
    

    @classmethod
    def SetCommandLineEnv(cls, params:dict):
        '''👉️ Sets environment variables.

        Example:
            * Given: .SetCommandLineEnv({a:x}, {b:y})
            * When: print(os.environ['b'])
            * Then: 'y'
        '''
        for param in params:
            os.environ[param] = params[param]
    

    @classmethod
    def CurrentDirectory(cls):
        '''👉️ Returns the current directory.'''
        from .DIRECTORY import DIRECTORY
        return DIRECTORY.GetCurrent()
    
    
    @classmethod
    def Directory(cls, path):
        '''👉️ Wrapper for a directory in the operating system.'''
        from .FILESYSTEM import FILESYSTEM
        return FILESYSTEM.DIRECTORY(path)
        

    @classmethod
    def File(cls, path):
        '''👉️ Wrapper for a file in the operating system.'''
        from .FILESYSTEM import FILESYSTEM
        return FILESYSTEM.FILE(path)
    

    @classmethod
    def Calculate(cls, cmd):
        '''👉  Executes a command line and returns the result.'''
        import subprocess
        LOG.Print('@: Executing ' + cmd)
        answer = subprocess.check_output(cmd, shell=True)
        return answer.decode("utf-8").strip()
    
    
    @classmethod
    def Execute(cls, cmd:str) -> str:
        '''👉  Executes a command line.'''
        import subprocess
        LOG.Print(f'@: Executing', cmd)
        
        if type(cmd) == str:
            answer = subprocess.Popen(cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE)

        elif type(cmd) == list:
            answer = subprocess.Popen(cmd, 
                shell=False,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE)

        else:
            raise Exception('Invalid command type')
        
        answer.wait()
        if answer.returncode == 0:
            LOG.Print("@: Command executed successfully!", answer.stdout)
        else:
            LOG.RaiseException("@: Error:", answer.stderr)

        ret = answer.stdout.read().decode('utf-8')
        return ret
    

    @classmethod
    def ExecuteShellLess(cls, cmds:list[str]):
        '''👉  Executes a command line without shell.'''
        import subprocess
        LOG.Print('@: Executing ', cmds)
        answer = subprocess.Popen(cmds, shell=False)
        answer.wait()


    @classmethod
    def Execute3(cls, cmds:list[str]):
        # Execute the command
        import subprocess
        result = subprocess.run(cmds, 
            shell=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True)

        # Check if the command was executed successfully
        if result.returncode == 0:
            LOG.Print("Command executed successfully!", result.stdout)
        else:
            LOG.RaiseException("Error:", result.stderr)


    @classmethod
    def ExecuteMany(cls, cmds:list[str]):
        '''👉 Executes many commands.'''
        for cmd in cmds:
            cls.Execute(cmd)


    @classmethod
    def GetCommandLineArg(cls, name:str, optional=False):
        '''👉️ Returns the value of a command line argument.'''
        args = cls.GetCommandLineArgs()
        ret = args.GetStr(name)
        if not optional and ret == None:
            LOG.RaiseException(f'Missing command line argument: {name}')
        return ret 


    @classmethod
    def GetCommandLineArgs(cls):
        '''👉️ Returns the arguments passed to the script.
        * The args should be passed as <name>:<value> pairs.
        * Example: python3 my-script.py arg1:val1 argN:valN
        '''

        args = {}
        import sys

        for arg in sys.argv:
            if ':' in arg:
                name = arg.split(':')[0]
                value = arg.split(':')[1]
                args[name] = value
                
        from .STRUCT import STRUCT
        return STRUCT(args)
    

    @classmethod
    def Unzip(cls, file:str, into:str):
        '''👉️ Unzips a file.
        
        Arguments:
            * `file` {str} -- The file to unzip.
            * `into` {str} -- The directory to unzip into.
        '''
        zip = cls.File(file).RequirePath()
        dir = cls.Directory(into).RequirePath()
        cmd = f'unzip -o -q {zip} -d {dir}'
        cls.Execute(cmd)


    @classmethod
    def GetClassDirectory(cls, obj):
        '''👉️ Returns the directory of a given class.'''

        # Step 1: Get the module name
        module_name = obj.__module__

        # Step 2: Get the module object
        import sys
        module_object = sys.modules[module_name]

        # Step 3: Get the file path of the module
        file_path = module_object.__file__

        # Step 4: Get the directory from the file path
        path = os.path.dirname(file_path)
        return cls.Directory(path)
    

    @classmethod
    def GetClassFile(cls, obj:any|type):
        '''👉️ Returns the file where a given class is defined.
        
        Argumens:
         * `obj` {any} -- The class object.
        '''

        if obj == None:
            LOG.RaiseException('Invalid class object.')

        if obj is type:
            return cls.File(obj.__file__)
        
        # Step 1: Get the module name
        module_name = obj.__module__

        # Step 2: Get the module object
        import sys
        module_object = sys.modules[module_name]

        # Step 3: Get the file path of the module
        return cls.File(module_object.__file__)
    

    @classmethod
    def GetFileInClass(cls, obj, 
        name:str=None
    ):
        '''👉️ Returns the file of a given class.
        
        Argumens:
         * `obj` {any} -- The class object.
         * `name` {str} -- The file name inside the directory of the class.
        '''

        if name:
            for file in cls.GetClassDirectory(obj).GetDeepFiles():
                if name == file.GetSimpleName():
                    return file
            LOG.RaiseException(f'File not found: {name}')


    @classmethod
    def GetDirectoryInClass(cls, obj, 
        name:str=None
    ):
        '''👉️ Returns the directory of a given class.
        
        Argumens:
         * `obj` {any} -- The class object.
         * `name` {str} -- The directory name inside the directory of the class.
        '''

        if name:
            for dir in cls.GetClassDirectory(obj).GetDeepDirs():
                if name == dir.GetSimpleName():
                    return dir
            LOG.RaiseException(f'Directory not found: {name}')
    

    @classmethod
    def Environment(cls, name: str):
        '''👉️ Returns a configuration from os.environ, 
        i.e. same as 'os.environ[name]'.'''
        import os
        if name not in os.environ:
            LOG.RaiseException(f'Environment variable {name} is not set.')
        return os.environ[name]
    

    @classmethod
    def ReadFileBytes(cls, path:str):
        '''👉️ Returns the bytes of a file.'''
        # Open the zip file in binary read mode
        with open(path, 'rb') as file:
            zip_bytes = file.read()
        return zip_bytes
        

    @classmethod
    def ClearScreen(cls):
        '''👉️ Clears the screen.'''
        import os
        os.system('cls' if os.name == 'nt' else 'clear')


    @classmethod
    def GetProcessID(cls) -> int:
        '''👉️ Returns the process ID.'''
        import os
        return os.getpid()
