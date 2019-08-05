import json
from HttpTesting.base.base_config import BaseConfig
from HttpTesting.library.scripts import (
    get_datetime_str, 
    retry, 
    get_yaml_field
    )
import requests
from requests.exceptions import (HTTPError, ConnectionError, ConnectTimeout)
from HttpTesting.globalVar import gl
from HttpTesting.library.Multipart import MultipartFormData
#########################################################################
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#Remove warnings when SSL is turned off dueto requests.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
###########################################################################
class HttpWebRequest(object):
    """
    HTTP post requests or get requests.
    usage:
        #instance class 
        http = HttpWebRequest()

        res = http.get(**kwargs)
        
        res = http.post(**kwargs)
    """
    def __init__(self):
        self.config  = get_yaml_field(gl.configFile)
        self.baseUrl  = BaseConfig.base_url()
        self.OUT_TMPL = """{0}:\n{1} {2}请求:{3}\n请求:\n{4}\n响应:"""

    def header_lower(self, hdict):
        """
        Convert HTTP header information to lowercase.
        param:
            hdict: Head dictionary type.
        usage:
            ret = header_lower(hdict)
        return:
            dict Head dictionary type.
        """
        tmp = {}
        for key, val in hdict.items():
            tmp[str(key).lower()] = str(val).lower()
        return tmp 


    @retry(reNum=3)
    def get(self, **kwargs):
        """
        Get requests.
        Param:
            **kwargs Request dictionary object.
        Usage:
            http = HttpWebRequest()
            res, headers, cookie, result = http.get(**kwargs)
        Return:
            res: Request object.
            headers: Response headers object.
            cookie: Request cookie.
            result: Request results result.json() or result.text
        """

        #Whether to adopt , url = base_url + url
        if self.config['ENABLE_BASE_URL']:
            url = '{}{}'.format(self.baseUrl, str(kwargs['gurl']).strip())
        else:
            url = str(kwargs['gurl']).strip()

        #format output.
        params = json.dumps(kwargs['params'], sort_keys=True, indent=4)
        #Report output template.   
        tmpl = self.OUT_TMPL.format(
            kwargs['desc'],
            get_datetime_str(),
            kwargs['method'],
            url,
            params
        )
        print(tmpl)    

        try:
            res =requests.request(kwargs['method'], url, params=kwargs['params'], headers=kwargs['headers'], verify=False)
            headers = res.headers
            cookie = res.cookies.get_dict()
            if res.status_code ==200:
                if 'json' in headers['Content-Type']:
                    result = res.json()
                else:
                    result = res.text
            else:
                result =  {"errcode": 9001, "errmsg": str(res)}

        except (HTTPError, ConnectionError, ConnectTimeout) as ex:
            result = {"errcode": 9002, "errmsg": str(ex)}
        except Exception as ex:
            result = {"errcode": 9003, "errmsg": str(ex) }

        tmpl_result = json.dumps(result, sort_keys=True, indent=4, ensure_ascii=False)
        print(tmpl_result) #The Response results are output to the report.
        return res, headers, cookie, result


    # Post Request
    @retry(reNum=3)
    def post(self, **kwargs):
        """post请求"""
 
        #Whether to adopt , url = base_url + url
        if self.config['ENABLE_BASE_URL']:
            url = '{}{}'.format(self.baseUrl, str(kwargs['gurl']).strip())
        else:
            url = str(kwargs['gurl']).strip()

        data = kwargs['data']
        
        #format output
        tmpl_data = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
        #Report output template. 
        tmpl = self.OUT_TMPL.format(
            kwargs['desc'],
            get_datetime_str(),
            kwargs['method'],
            url,
            tmpl_data
        )
        print(tmpl)

        header_dict = self.header_lower(kwargs['headers'])
        try:
            #Convert the data to form-data.
            if 'form-data' in header_dict['content-type']:
                data = MultipartFormData.to_form_data(data, headers=kwargs['headers'])
                res = requests.request(
                    kwargs['method'], 
                    url, 
                    data=data.encode(), 
                    headers=kwargs['headers'],
                    verify= False
                    )
            elif 'application/json' in header_dict['content-type']:
                res = requests.request(
                    kwargs['method'], 
                    url, 
                    json=data, 
                    headers=kwargs['headers'],
                    verify= False
                    )
            elif 'application/x-www-form-urlencoded' in header_dict['content-type']:
                res = requests.request(
                    kwargs['method'], 
                    url, 
                    data=data, 
                    headers=kwargs['headers'],
                    verify= False
                    )                
            else:
                res = requests.request(
                    kwargs['method'], 
                    url, 
                    params=data, 
                    headers=kwargs['headers'],
                    verify= False
                    )

            headers = res.headers
            cookie = res.cookies.get_dict()

            if res.status_code ==200:
                if 'json' in headers['Content-Type']:
                    result = res.json()
                else:
                    result = res.text
            else:
                result =  {"errcode": 9001, "errmsg": str(res)}

        except (HTTPError, ConnectionError, ConnectTimeout) as ex:
            result =  {"errcode": 9002, "errmsg": str(ex)}
        
        # format output.
        tmpl_result = json.dumps(result, sort_keys=True, indent=4, ensure_ascii=False)
        #The Response results are output to the report.
        print(tmpl_result) 

        return res, headers, cookie, result





