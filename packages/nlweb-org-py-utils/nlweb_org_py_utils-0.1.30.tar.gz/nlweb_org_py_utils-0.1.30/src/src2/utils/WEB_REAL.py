# 📚 WEB

import json
from urllib import request
from urllib.request import urlopen
from .STRUCT import  STRUCT
from .LOG import LOG
from .WEB_BASE import WEB_BASE


class WEB_REAL(WEB_BASE): 
    ''' 👉️ Generic web-related methods.'''


    @classmethod
    def HttpPost(cls, url: str, body: any) -> STRUCT:
        ''' 👉️ Executes a POST request.
        * https://stackoverflow.com/questions/36484184/python-make-a-post-request-using-python-3-urllib  '''
    
        LOG.Print(f'🌐 WEB.Real.HttpPost()', f'{url=}', body)

        # data = parse.urlencode(body).encode()
        # LOG.Print(f'{data=}')
        data = bytes(json.dumps(body), encoding='utf-8')
        
        req = request.Request(url=url, method='POST', data=data)
        req.add_header('Content-Type', 'application/json')
        resp = request.urlopen(req)
        
        charset= resp.info().get_content_charset()
        if charset == None:
            charset = 'utf-8'
        content=resp.read().decode(charset)
        
        LOG.Print(f'🌐 WEB.Real.HttpPost.return...', content)
        return STRUCT(content)


    @classmethod
    def HttpGet(cls, url: str) -> str:
        ''' 👉️ Executes a GET request.
         * https://stackoverflow.com/questions/37819525/lambda-function-to-make-simple-http-request/71127429#71127429 '''
        
        LOG.Print(f'🌐 WEB.Get()', f'{url=}')

        with urlopen(url) as response:
            body = response.read()
        return body
    
    

