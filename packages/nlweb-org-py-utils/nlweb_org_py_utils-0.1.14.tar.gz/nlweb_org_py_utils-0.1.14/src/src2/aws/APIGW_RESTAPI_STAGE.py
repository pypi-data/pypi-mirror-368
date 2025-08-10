# 📚 API Gateway

from LOG import LOG
from PRINTABLE import PRINTABLE
from STRUCT import STRUCT


class APIGW_RESTAPI_STAGE(PRINTABLE):
    '''👉️ Represents a stage for a REST API in API GATEWAY.'''
    
    ICON = '🅰️'
    

    def __init__(self, 
        api, 
        name:str, 
        client,
        webAclArn:str= None
    ) -> None:
        '''👉️ Initializes a new APIGW_RESTAPI_STAGE object.'''
        LOG.Print('@')

        from APIGW_RESTAPI import APIGW_RESTAPI
        self.Api:APIGW_RESTAPI = api
        self.ApiID = self.Api.ID
        self.Name = name
        self.Endpoint = self.Api.Endpoint
        self.WebAclArn = webAclArn
        self.Arn = f'arn:aws:apigateway:{self.Api.Region}::/restapis/{self.Api.ID}/stages/{name}'

        self.Client = client

        PRINTABLE.__init__(self, lambda: {
            'ApiID': self.Api.ID, 
            'Name': self.Name,
            'Endpoint': self.Endpoint
        })


    def RequireApiID(self):
        '''👉️ Returns the API ID.'''
        return self.ApiID


    def RequireName(self):
        '''👉️ Returns the name of the stage.'''
        return self.Name


    def RequireEndpoint(self):
        '''👉️ Returns the endpoint.'''
        return self.Endpoint
    

    def RequireEndpointUrl(self):
        '''👉️ Returns the endpoint with the stage.'''
        return f'https://{self.Endpoint}/{self.Name}'
    

    def RequireEndpointUrlWithoutStage(self):
        '''👉️ Returns the endpoint without the stage.'''
        return f'https://{self.Endpoint}'
    

    def RequireEndpointUrlWithoutStageOrProtocol(self):
        '''👉️ Returns the endpoint without the stage or protocol.'''
        return f'{self.Endpoint}'
    
