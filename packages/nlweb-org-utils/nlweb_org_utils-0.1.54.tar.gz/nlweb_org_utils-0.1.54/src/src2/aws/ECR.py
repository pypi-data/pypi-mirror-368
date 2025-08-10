from __future__ import annotations
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from DIRECTORY import DIRECTORY
from ECR_REPO import ECR_REPO
from LOG import LOG
from UTILS import UTILS

import boto3
client = boto3.client('ecr')

class ECR(AWS_RESOURCE_POOL[ECR_REPO]):


    @classmethod
    def Ensure(cls, 
        name:str
    ):
        return super()._Ensure(
            name= name.lower())        
    
    
    @classmethod
    def Create(cls, name:str):
        '''👉 Creates a new ECR repository.'''
        LOG.Print(f'@ Creating ECR repository {name=}')

        if name != name.lower():
            LOG.RaiseException('ECR repository name must be lowercase')

        ecr_response = client.create_repository(
            repositoryName= name)
        
        repo = ECR_REPO(
            pool= cls,
            client= client,
            meta= ecr_response['repository'])
        
        return repo


    @classmethod
    def List(cls):
        '''👉 Gets the list of repositories.'''

        response = client.describe_repositories()
        
        ret = []
        for repo in response['repositories']:

            item = ECR_REPO(
                pool= cls,
                client= client,
                meta= repo)
            ret.append(item)
            
        return ret
    

    