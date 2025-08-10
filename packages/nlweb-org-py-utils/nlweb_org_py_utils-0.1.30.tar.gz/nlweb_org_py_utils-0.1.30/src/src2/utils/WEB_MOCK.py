# 📚 WEB

from .LOG import LOG
from .TESTS import  TESTS
from .UTILS_OBJECTS import  UTILS_OBJECTS
from .AWS_TEST import AWS_TEST
from .NLWEB import NLWEB
from .LOG import LOG
from .TESTS import  ValidationException

import json

from .WEB_BASE import WEB_BASE, UrlNotFoundException


class UrlNotMockedException(ValidationException, UrlNotFoundException):
    pass


class WEB_MOCK(WEB_BASE):

    ICON= '🌐'

    UseRealManifests = False
    _internet:dict[str,object] = {}
    _domains: list[str] = []


    @classmethod
    def ResetWebMock(cls):
        ##LOG.Print(f'\nWEB_MOCK.ResetMock()')

        WEB_MOCK._internet = {}
        WEB_MOCK._domains = []


    @staticmethod
    def HelloWorld(request:any=None):
        return {
            'Name': 'Hello World!'
        }


    @classmethod
    def MockUrl(cls, url:str, domain:str, handler:object=HelloWorld):
        LOG.Print(cls.MockUrl, f'{url=}', f'{domain=}')

        if url.startswith('https://dns.google/resolve?name=nlweb._domainkey'):
            LOG.RaiseException('Google DNS URLs do not need to be mocked!')

        if domain not in WEB_MOCK._domains:
            WEB_MOCK._domains.append(domain)

        WEB_MOCK._internet[url] = {
            'Handler': handler,
            'Domain': domain,
            'Url': url
        }
        ##LOG.Print(f'{WEB_MOCK._internet=}')

        #Check
        if cls._GetMock(url)['Handler'] != handler:
            LOG.RaiseException('Unexpected behaviour!')


    @classmethod
    def MockGoogle(cls):
        ret = {
            "AD": True,
            "Answer": [{
                "type": 16,
                "data": "v=DKIM1; k=rsa; p=pub"
            }]
        }
        return json.dumps(ret)


    @classmethod
    def _GetMock(cls, url: str) -> dict[str,any]:
        LOG.Print(cls._GetMock, f'{url=}')

        if url.startswith('https://dns.google/resolve?name=nlweb._domainkey.'):
            return cls.MockGoogle()
        
        if url not in WEB_MOCK._internet:
            LOG.Print(cls._GetMock, f': {WEB_MOCK._internet=}')
            ##LOG.Print(f'  WEB_MOCK.{url=}')

            if not WEB_MOCK.UseRealManifests: 
                if url.startswith('https://nlweb.') and url.endswith('/manifest'):
                    domain = url.replace('https://nlweb.', '').replace('/manifest', '')
                    from .MANIFEST_MOCKS import MANIFEST_MOCKS
                    return MANIFEST_MOCKS.MockManifest(domain=domain).ToYaml()
             
            existing = [x for x in WEB_MOCK._domains]
            existing.sort()
            LOG.RaiseUrlNotFoundException (
                f'404, URL not found on our mocked internet {url}! ',
                f'URL= {url}',
                f'Domain= {NLWEB.CONFIG().RequireDomain()}', 
                f'Map=', existing)
    
        item = WEB_MOCK._internet[url]
        return item
    

    @classmethod
    def HttpGet(cls, url: str) -> str:
        ''' 👉️ Executes a mocked GET request.'''
        LOG.Print(cls.HttpGet, f'{url=}')
        
        if not url.startswith('https://'):
            LOG.RaiseValidationException(
                f'URLs must start with https://, but received [{url}]!')
        
        mock = cls._GetMock(url)
        if isinstance(mock, str):
            return mock
        
        if 'Handler' not in mock:
            LOG.RaiseException(f'Handler not found in mock={mock}')
        handler = mock['Handler']

        domain1 = NLWEB.CONFIG().RequireDomain(optional=True)
        domain2 = cls._domainFromUrl(url)
        
        AWS_TEST.SetDomain(domain2)
        result = handler(url)
        AWS_TEST.SetDomain(domain1)
        
        ##LOG.Print(f'UTILS.WEB().HttpGet().{result=}')

        if isinstance(result, dict):
            return json.dumps(result)
        else:
            return result
    

    @classmethod
    def HttpPost(cls, url:str, body:dict) -> str:
        ''' 👉️ Executes a mocked POST request.'''

        LOG.Print(cls.HttpPost, f'{url=}', body)
        ##LOG.Print(f'WEB_MOCK.HttpPost(url={url})')

        UTILS_OBJECTS.RequireArgs([url, body])
        
        if not url.startswith('https://'):
            LOG.RaiseValidationException(f'URLs must start with https://, but received [{url}]!')
        
        mock = cls._GetMock(url)
        payload = json.loads(json.dumps(body))
        
        payload = json.loads(json.dumps(payload))
        ##LOG.Print(f'\nWEB_MOCK.HttpPost(): payload={payload})')

        domain1 = NLWEB.CONFIG().RequireDomain(optional=True)
        domain2 = cls._domainFromUrl(url)
        
        AWS_TEST.SetDomain(domain2)
        result = mock['Handler'](payload)
        ##LOG.Print(f'  WEB_MOCK.HttpPost(): result={result})')
        AWS_TEST.SetDomain(domain1)

        if isinstance(result, dict):

            if 'body' in result:
                result = json.loads(result['body'])
            if 'Insights' in result:
                del result['Insights']

            return json.dumps(result)
        else:
            return result


    @classmethod
    def _domainFromUrl(cls, url:str):
        if not '/inbox' in url \
        and not '/manifest' in url \
        and not '/selfie' in url:
            return None
        else:
            return url.replace('https://nlweb.', ''
                ).replace('/inbox',''
                ).replace('/manifest',''
                ).replace('/selfie','')
            

    @classmethod
    def MockDomainManifest(cls, domain:str, handler:object=TESTS._echo):
        ''' The request comes from the internet.'''
        LOG.Print(cls.MockDomainManifest, f'{domain=}')

        url= f'https://nlweb.{domain}/manifest'

        cls.MockUrl(
            url= url,
            handler= handler,
            domain= domain)

        
    @classmethod
    def MockDomain(cls, domain:str, handler:object=TESTS._echo):
        ''' The request comes from the internet.'''
        LOG.Print(cls.MockDomain, f'{domain=}')

        url= f'https://nlweb.{domain}/inbox'

        if url in WEB_MOCK._internet:
            if WEB_MOCK._internet[url]['Handler'] != TESTS._echo:
                return # Ignoring an echo if the domain has alredy been properly set up.
                ##LOG.Exception(f'Reseting an inbox to echo is not allower! domain={domain}')

        cls.MockUrl(
            url= url,
            handler= handler,
            domain= domain)
        

    @classmethod
    def IsDomainMocked(cls, domain:str):
        return domain in WEB_MOCK._domains
    

    @classmethod
    def DumpDomains(self):
        '''👉 Prints the item IDs.'''
        
        LOG.Print(self.DumpDomains)
        domains = WEB_MOCK._domains
        domains.sort()
        
        LOG.Print(self.DumpDomains, f':', domains)