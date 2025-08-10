import boto3
client = boto3.client('codedeploy')

from CODEDEPLOY_APP import CODEDEPLOY_APP
from UTILS import UTILS
from LOG import LOG


class CODEDEPLOY:
    
    
    def CreateApplication(self, 
        name:str, 
        compute_platform:str='ECS'
    ) -> dict:
        '''👉 Creates a new CodeDeploy application.'''
        
        response = client.create_application(
            applicationName= name,
            computePlatform= compute_platform)
        
        meta = response['application']
        return CODEDEPLOY_APP(
            meta= meta)


    def GetApplication(self,
        name:str
    ) -> dict:
        '''👉 Gets the application.'''

        response = client.get_application(
            applicationName= name)
        
        return CODEDEPLOY_APP(
            client= client,
            meta= response['application'])
    

    