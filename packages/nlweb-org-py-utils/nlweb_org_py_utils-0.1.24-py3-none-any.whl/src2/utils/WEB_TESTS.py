# 📚 WEB

from AWS_TEST import AWS_TEST
from WEB_MOCK import  WEB_MOCK


class WEB_TESTS(WEB_MOCK, AWS_TEST): 


    @classmethod
    def _testGetMethodStr(cls, request:dict):
        return "dummy"
    
    @classmethod
    def _testGetMethodDict(cls, request:dict):
        return {'A':1}

    @classmethod
    def TestHttpGet(cls):
        
        url = 'https://any-domain.com/get/'

        
        # Registered STR.
        cls.ResetWebMock()
        cls.MockUrl(
            url= url+'1', 
            handler= cls._testGetMethodStr,
            domain= 'any-domain.com')
        ret = cls.HttpGet(url+'1')
        
        # Unregistered.
        cls.HttpGet(url+'1')
        with cls.AssertValidation():
            cls.HttpGet(url)
        cls.ResetWebMock()
        with cls.AssertValidation():
            cls.HttpGet(url+'1')
        with cls.AssertValidation():
            cls.HttpGet(url)

        
        cls.AssertClass(ret, str)
        cls.AssertEqual(ret, 'dummy')

        # Registered OBJ.
        cls.ResetWebMock()
        cls.MockUrl(
            url= url+'2', 
            handler= cls._testGetMethodDict,
            domain= 'any-domain.com')
        ret = cls.HttpGet(url+'2')

        cls.AssertClass(ret, str)
        cls.AssertEqual(ret, '{"A": 1}')
    
        # Not started with https://
        cls.ResetWebMock()
        url = 'any-domain.com/get'
        cls.MockUrl(
            url= url, 
            handler= cls._testGetMethodStr,
            domain= 'any-domain.com')
        with cls.AssertValidation():
            cls.HttpGet(url)


    @classmethod
    def _testPostMethodStr(cls, event:any):
        return f"Received={event}"
    
    @classmethod
    def _testPostMethodObj(cls, event:any):
        return {'Received':event}

    @classmethod
    def TestHttpPost(cls):
        
        url = 'https://any-domain.com/post'

        # Unregistered.
        cls.ResetWebMock()
        with cls.AssertValidation():
            cls.HttpPost(url=url, body='')

        # Registered STR.
        cls.ResetWebMock()
        cls.MockUrl(
            url= url+'1', 
            handler= cls._testPostMethodStr,
            domain= 'any-domain.com')
        ret = cls.HttpPost(url=url+'1', body='dummy')

        cls.AssertClass(ret, str)
        cls.AssertEqual(ret, 'Received=dummy')

        # Registered OBJ.
        cls.ResetWebMock()
        cls.MockUrl(
            url= url+'2', 
            handler= cls._testPostMethodObj,
            domain= 'any-domain.com')
        ret = cls.HttpPost(url=url+'2', body={'B':1})

        cls.AssertClass(ret, str)
        expected = '{"Received": {"B": 1}}'
        cls.AssertEqual(ret, expected)
    
        # Not started with https://
        cls.ResetWebMock()
        url = 'any-domain.com/post'
        cls.MockUrl(
            url= url, 
            handler= cls._testPostMethodStr,
            domain= 'any-domain.com')
        with cls.AssertValidation():
            cls.HttpPost(url=url, body='')


    @classmethod
    def TestHttpGetJson(cls):
        url = 'https://any-domain.com/'
        
        cls.ResetWebMock()
        cls.MockUrl(
            url=url, 
            handler= cls._testGetMethodDict,
            domain= 'any-domain.com')
        
        ret = cls.HttpGetJson(url)
        cls.AssertClass(ret, dict)
        cls.AssertEqual(ret, {'A':1})


    @classmethod
    def TestHttpGetImage(cls):
        pass
    

    @classmethod
    def TestHttpGetImageQR(cls):
        pass
    

    @classmethod
    def TestHttpResponse(cls):
        cls.AssertEqual(
            given= cls.HttpResponse(status=200, body={'A':1}, format='json'),
            expect= {
                "statusCode": 200,
                "body": "{\"A\": 1}"
            })
        
        {'statusCode': 200, 'body': '{"A": 1}'}
        {'statusCode': 200, 'body': '{"A", 1}'}

        cls.AssertEqual(
            given= cls.HttpResponse(status=400, body={'B':2}, format='yaml'), 
            expect= {
                "statusCode": 400,
                "body": "B: 2",
                "headers": {
                    "content-type": 'application/x-yaml'
                }
            })

        cls.AssertEqual(
            given= cls.HttpResponse(status=400, body='{B:2}', format='text'),
            expect= {
                "statusCode": 400,
                "body": "{B:2}"
            })
    

    @classmethod
    def TestAllWeb(cls):
        cls.TestHttpGet()
        cls.TestHttpPost()
        cls.TestHttpGetJson()
        cls.TestHttpGetImage()
        cls.TestHttpGetImageQR()
        cls.TestHttpResponse()

    