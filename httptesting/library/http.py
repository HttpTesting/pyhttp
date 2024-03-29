import json
from httptesting.library.scripts import (
    get_datetime_str,
    print_font_color
    )
import requests
from requests.exceptions import (HTTPError, ConnectionError, ConnectTimeout)
from httptesting.library import gl
from httptesting.library.config import conf
from httptesting.library.Multipart import MultipartFormData
#########################################################################
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# Remove warnings when SSL is turned off queto requests.
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
        self.config = conf.get_yaml_field(gl.configFile)
        self.base_url = self.config['BASE_URL']
        self.OUT_TMPL = """{0} {1}请求:{2}\n请求:\n{3}\n响应:"""

    @staticmethod
    def headers_to_lower(headers):
        """
        Convert HTTP header information to lowercase.
        param:
            headers: Head dictionary type.
        usage:
            ret = headers_to_lower(headers)
        return:
            dict Head dictionary type.
        """
        return {str(key).lower(): str(val).lower() for key, val in headers.items()}

    def _wisdom_url_mode(self, kwargs):
        """
        Wisdom to choose url.

        Return: 
            url
        """
        # Whether to adopt , url = base_url + url
        if self.config['ENABLE_WISDOM_MODE']:
            if 'http://' in str(kwargs['gurl']) or 'https://' in str(kwargs['gurl']):
                url = str(kwargs['gurl']).strip()
            else:
                url = '{}{}'.format(self.base_url, str(kwargs['gurl']).strip())

        elif self.config['ENABLE_BASE_URL']:
            url = '{}{}'.format(self.base_url, str(kwargs['gurl']).strip())
        else:
            url = str(kwargs['gurl']).strip()

        return url

    def _print_mode_tmpl(self, kwargs, params):
        """
        Print mode and template.
        """
        url = self._wisdom_url_mode(kwargs)
        # console print color
        if self.config['ENABLE_EXEC_MODE']:
            print_font_color('{}:'.format(kwargs['desc']), color='green')
        else:
            print(kwargs['desc'])
        # Report output template.   
        tmpl = self.OUT_TMPL.format(
            get_datetime_str(),
            kwargs['method'],
            url,
            params
        )
        print(tmpl)

    @staticmethod
    def _request_header_type(header_dict, url, data, kwargs):
        """
        Select request content-type
        """
        # Convert the data to form-data.
        if 'form-data' in header_dict['content-type']:
            data = MultipartFormData.to_form_data(data, headers=kwargs['headers'])
            res = requests.request(
                kwargs['method'],
                url,
                data=data.encode(),
                headers=kwargs['headers'],
                verify=False
                )
        elif 'application/json' in header_dict['content-type']:
            res = requests.request(
                kwargs['method'],
                url,
                json=data,
                headers=kwargs['headers'],
                verify=False
                )
        elif 'application/x-www-form-urlencoded' in header_dict['content-type']:
            res = requests.request(
                kwargs['method'],
                url,
                data=data,
                headers=kwargs['headers'],
                verify=False
                ) 
        else:
            res = requests.request(
                kwargs['method'],
                url,
                params=data,
                headers=kwargs['headers'],
                verify=False
                )
        return res

    @staticmethod
    def _header_content_type_lcase(header_dict):
        """
        The Replace key-value in dict 
        """
        if 'Content-Type' in header_dict.keys():
            header_dict['content-type'] = header_dict['Content-Type']
            header_dict.pop('Content-Type')
            return header_dict

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
        res, headers, cookie = None, None, None

        try:
            params = eval(kwargs['params'])
        except (TypeError, ValueError):
            params = kwargs['params']

        # Whether to adopt , url = base_url + url
        url = self._wisdom_url_mode(kwargs)

        # format output.
        params_dumps = json.dumps(params, sort_keys=True, indent=4)
        # console print color
        self._print_mode_tmpl(kwargs, params_dumps)

        try:
            res = requests.request(kwargs['method'], str(url), params=params, headers=kwargs['headers'], verify=False)
            headers = res.headers
            cookie = res.cookies.get_dict()
            if res.status_code == 200:
                try:
                    result = res.json()
                except:
                    result = res.text
            else:
                result = {"errcode": 9001, "errmsg": str(res)}

        except (HTTPError, ConnectionError, ConnectTimeout) as ex:
            result = {"errcode": 9002, "errmsg": str(ex)}
        except Exception as ex:
            result = {"errcode": 9003, "errmsg": str(ex)}

        tmpl_result = json.dumps(result, sort_keys=True, indent=4, ensure_ascii=False)
        # The Response results are output to the report.
        print(tmpl_result)
        return res, headers, cookie, result

    # Post Request
    def post(self, **kwargs):
        """post请求"""
        headers, cookie, res = None, None, None

        # Whether to adopt , url = base_url + url
        url = self._wisdom_url_mode(kwargs)

        try:
            data = eval(kwargs['data'])
        except (TypeError, ValueError):
            data = kwargs['data']

        # format output
        tmpl_data = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
        # console print color
        self._print_mode_tmpl(kwargs, tmpl_data)

        header_dict = self.headers_to_lower(kwargs['headers'])
        try:
            # Convert the data to form-data.
            res = self._request_header_type(header_dict, url, data, kwargs)

            headers = res.headers
            cookie = res.cookies.get_dict()

            if res.status_code == 200:
                try:
                    result = res.json()
                except:
                    result = res.text
            else:
                result = {"errcode": 9001, "errmsg": str(res)}

        except (HTTPError, ConnectionError, ConnectTimeout) as ex:
            result = {"errcode": 9002, "errmsg": str(ex)}

        # format output.
        tmpl_result = json.dumps(result, sort_keys=True, indent=4, ensure_ascii=False)
        # The Response results are output to the report.
        print(tmpl_result) 

        return res, headers, cookie, result


# singleton mode.
req = HttpWebRequest()
