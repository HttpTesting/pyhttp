import time
import os
import io
import random
import re
import socket
import collections
import yaml
from functools import wraps
import requests
from HttpTesting.globalVar import gl
from requests.exceptions import (
    ConnectTimeout,
    ConnectionError,
    Timeout,
    HTTPError
    )
from HttpTesting.library.case_queue import case_exec_queue


# Datetime string.
def get_datetime_str():
    """
    Randrom time string.
    return:
        Time string.
    """
    time.sleep(0.5)
    datetime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    return datetime


@property
def get_timestamp_int():
    """
    Second timestamp.
    usage:
        ret = get_timestamp_int()
    return:
        integer timestamp.
    """
    return int(time.time())


# Write YAML file content.
def write_ymal(path,data):
    """
    Write YAML file content.
    param:
        path: YAML file content.
        data: Dictionary type data.
    usage:
        write_yaml(r'd:\template.yaml', data)
    return:
        There is no.
    """
    with open(path, 'wb') as fp:
        yaml.dump(data, fp)


# Read YAML file.
def get_yaml_field(path):
    """
    Gets the YAML configuration file content.
    param:
        path: YAML file path.
    usage:
        ret_dict = get_yaml_field(path)
    return:
        ret_dict is all of YAML's content.
    """
    with open(path, 'rb') as fp:
        cont = fp.read()

    ret = yaml.load(cont, Loader=yaml.FullLoader)
    return ret


# Get the flag in the configuration file.
def get_run_flag(skey):
    """
    Get the flag in the configuration file.
    param:
        skey: flag
    usage:
        ret = get_run_flag('Flag')
    return:
        ret: 'Y' or 'N'
    """
    yaml_dict = get_yaml_field(gl.exeConfigFile)
    ret_flag = yaml_dict['RUNING'][skey]['Flag']
    return ret_flag


def load_case_data(flag='TEST_CASE'):
    """
    :Desc:
        load DDT data form YAML.
    :param flag:
        The starting node of the interface case in YAML.
        default:
            TEST_CASE
    :import
        from HttpTesting.library.scripts import load_case_data
        or
        form HttpTesting.library import scripts
    :invoke
        load_case_data()
        or
        scripts.load_case_data()

    :return: [] DDT data list
    """
    ddtData = []

    for _ in range(0, case_exec_queue.qsize()):
        if not case_exec_queue.empty():
            case_name = case_exec_queue.get()

            # Read the case
            readYam = get_yaml_field(case_name)
            # yaml start the node，The default is TEST_CASE.
            dictCase = readYam[flag]

            # Loop through the configuration data under the node, 
            # so case begins the use case
            for key in dictCase:
                # What begins with a case in configuration data is considered a use case.
                if str(key).lower().startswith('case'):

                    #Organize DDT [] data, and each case is a dict object
                    ddtData.append(dictCase[key])
        else:
            raise Exception("The CASE execution queue is empty.")
    return ddtData


def retry(**kw):
    """
    Decorator HTTP request error retry.
    :param arg: ()tuples，Exception class
    :param kw: reNum = n；N is the number of retries
    :return: The function itself
    """
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            raise_ex = None
            for n in range(kw['reNum']):
                try:
                    ret = func(*args, **kwargs)
                    time.sleep(random.randint(1, 3))
                    return ret
                except (ConnectTimeout, ConnectionError, Timeout, HTTPError) as ex:
                    raise_ex = ex
                print('Retry the {0} time'.format(n))
            return ret
        return _wrapper
    return wrapper


def rm_dirs_files(dirpath):
    """
    Delete folder and all files.
    :param dirpath: The target path
    :return: no
    """
    listdir = os.listdir(dirpath)
    if listdir:
        for f in listdir:
            filepath = os.path.join(dirpath, f)
            if os.path.isfile(filepath):
                os.remove(filepath)
            if os.path.isdir(filepath):
                os.rmdir(filepath)


def send_msg_dding(msg, token, url=''):
    """
    Send the nail message text to the nail group.
    :param msg: Message text.
    :param token: Rebot token.
    :param url: Nail request url.
    :return: Response content
    """
    text = {
            "msgtype": "text", 
            "text": {
                "content": msg
            },
            # "at": {
            #     "isAtAll": True
            # }
        }
    url_str = "{}{}".format(url, token)

    res = requests.request("POST", url_str, json=text)
    return res.json()


def get_sys_environ(name):
    """
    Gets the environment variable by name
    :param name: environment variable name
    :return:  Reverse an environment variable value
    """
    try:
        if name in os.environ:
            value = os.environ[name]
    except KeyError as ex:
        raise ex
    return value


def check_http_status(host, port, **kwargs):
    """
    Check that the  HTTP status is normal.
    :param host: The host address.
    :param port: The port number.
    :return bool: The return value is a Boolean.
    """
    url = 'http://{}:{}'.format(host, port)
    try:
        res = requests.request("GET", url, **kwargs)
        if res.status_code == 200:
            return True
    except Exception:
        return False


def parse_args_func(func_class, data):
    """
    Parse the function variables in the data.

    Args:
        func_class: FUNC  function object.
        data: Request data.

    Return:
        Replacement data.
    """
    data_bool = False
    if not isinstance(data, str):
        data_bool = True
        data = str(data)

    take = re.findall('\\%{.*?}\\%', data)

    for val in take:
        fStr = val.split("%{")[1][:-2]
        func = fStr.split('(')

        fName = func[0]
        fPara = func[1][:-1]

        if fPara == '':
            ret = getattr(func_class, fName)()
        else:
            ret = getattr(func_class, fName)(fPara)

        data = data.replace(val, str(ret))

    if data_bool:
        data = eval(data)
    return data


def write_file(filepath, mode, txt):
    """
    The write file.

    Args:
        filepath: File absolute path.
        mode: Read and Write.
        txt: text content.

    Usage:
        write_file('/xxxx/temp.txt', 'w', 'xxxxxx')

    Return:
        There is no.
    """
    with io.open(filepath, mode, encoding='utf-8') as fp:
        fp.write(txt)


def get_ip_or_name():
    """
    To obtain the local computer name or IP address.

    Args:

    Usage:
        addr, name = get_ip_or_name()

    Return:
        IP address, Computer name.
    """
    # Access to the local computer name.
    name = socket.getfqdn(socket.gethostname())
    # Access to the local computer address.
    addr = socket.gethostbyname(name)

    return addr, name


def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    """
    Convert the unordered dictionary to ordered and write yaml.
    param:
        data: 
        stream: 
        allow_unicode:
        default_flow_style:
        indent:
    return: There is no.
    """
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(collections.OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def ordered_yaml_load(yaml_path, Loader=yaml.Loader, object_pairs_hook=collections.OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    with open(yaml_path, 'r', encoding='utf-8') as fp:
        return yaml.load(fp.read(), OrderedLoader)


def write_case_to_yaml(yamFile, data):
    """
    Write the test case to yaml.
    param:
        yamFile: Yaml file path.
    return:
        There is no.
    """
    with io.open(yamFile, 'w', encoding='utf-8') as fp:
        ordered_dump(
            data,
            fp,
            Dumper=yaml.SafeDumper,
            allow_unicode=True,
            default_flow_style=False,
            indent=4
        )


def convert_yaml(yamlfile):
    """
    ReWrite YAML.
    """
    # YAML content dict.
    data = ordered_yaml_load(yamlfile)
    # Write YAML content.
    write_case_to_yaml(yamlfile, data)
    #
    print("Conversion to complete.")


def generate_case_tmpl(fileyaml):
    """
    Generate case template.

    param:
        fileyaml: yaml file path.

    usage:
        generate_case_tmpl(fileyaml)

    returns:
        There is no.
    """
    data = ordered_yaml_load(fileyaml)
    try:
        data['TEST_CASE']

        key = False
    except KeyError:
        key = True

    if key:

        d = collections.OrderedDict()
        d['Desc'] = '接口描述'
        d['Url'] = "https:/xxxxxx.xxxx/xxxx/xx"
        d['Method'] = "POST"
        d['Headers'] = {"content-type": "application/json;charset=UTF-8"}
        d['Data'] = data
        d['OutPara'] = ""
        d['Assert'] = []
        # case template.
        tmpl = {
            "TEST_CASE": {
                "Case1": [
                    {'Desc': '接口场景描述,报告描述'},
                    d
                ]
            }
        }
    else:
        tmpl = data
    # Write case to YAML file.
    write_case_to_yaml(fileyaml, tmpl)
    print("Conversion to complete.")


if __name__ == "__main__":
    env = get_ip_or_name()
    print(env)
