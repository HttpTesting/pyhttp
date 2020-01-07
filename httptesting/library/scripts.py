import time
import os
import io
import random
import socket
import collections
import yaml
import csv
from collections import OrderedDict
from yaml.parser import ParserError
from functools import wraps
import requests
from colorama import (Fore, Back, Style)
from httptesting.library import gl
from requests.exceptions import (
    ConnectTimeout,
    ConnectionError,
    Timeout,
    HTTPError
    )
from httptesting.library.case_queue import case_exec_queue


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
    try:
        with open(path, 'rb') as fp:
            cont = fp.read()

        ret = yaml.load(cont, Loader=yaml.FullLoader)
        return ret
    except ParserError as ex:
        raise Exception('YAML格式出错,错误信息: {}'.format(ex))


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

    try:
        with open(path, 'rb') as fp:
            cont = fp.read()

        ret = yaml.load(cont, Loader=yaml.FullLoader)
        return ret
    except ParserError as ex:
        raise Exception('YAML格式出错,错误信息: {}'.format(ex))


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


def sorted_data_fuction(dtlist, orderby):
    """
    Sorted case data.

    Example:
        dtlist =>
        [
            {"asc": 19, "name": 'yhleng', 'phone': 12398876},
            {"asc": 3, "name": 'yhleng', 'phone': 12398876},
            {"asc": 30, "name": 'yhleng', 'phone': 12398876},
            {"asc": 3, "name": 'yhleng', 'phone': 12398876}
        ]
        orderby => desc
        ret = sorted_data_fuction(dtlist) =>
        [
            {"asc": 3, "name": 'yhleng', 'phone': 12398876},
            {"asc": 3, "name": 'yhleng', 'phone': 12398876},
            {"asc": 19, "name": 'yhleng', 'phone': 12398876},
            {"asc": 30, "name": 'yhleng', 'phone': 12398876},
        ]  
    """
    for _num, val in enumerate(dtlist):

        for nk in range(0, len(dtlist)):
            # add Order default 0
            if ('Order' or 'order') not in dtlist[nk][0].keys():
                dtlist[nk][0]['Order'] = 0

            if orderby.lower() == 'desc':
                if dtlist[_num][0]['Order'] < dtlist[nk][0]['Order']:
                    dtlist[_num], dtlist[nk] = dtlist[nk], dtlist[_num]
            else:
                if dtlist[_num][0]['Order'] > dtlist[nk][0]['Order']:
                    dtlist[_num], dtlist[nk] = dtlist[nk], dtlist[_num]

    return dtlist


def load_case_data(flag='TEST_CASE'):
    """
    :Desc:
        load DDT data form YAML.
    :param flag:
        The starting node of the interface case in YAML.
        default:
            TEST_CASE
    :import
        from httptesting.library.scripts import load_case_data
        or
        form httptesting.library import scripts
    :invoke
        load_case_data()
        or
        scripts.load_case_data()

    :return: [] DDT data list
    """
    data_list = []
    temp_list = []
    case_path = None
    for _ in range(0, case_exec_queue.qsize()):
        if not case_exec_queue.empty():
            case_name = case_exec_queue.get()

            # OFF/ON Specify the execution case.
            parse_bool = False
            # Specify the execution CASE.
            if '&#' in case_name:
                parse_bool = True
                path_parse = case_name.split('&#')
                case_name = path_parse[0]
                path_parse.pop(0)

            # case path
            case_path = os.path.dirname(case_name)

            # Read the case
            read_yaml = get_yaml_field(case_name)
            # yaml start the node，The default is TEST_CASE.
            case_dict = read_yaml[flag]

            # OFF/ON Specify the execution case.
            if parse_bool:
                for case_name in path_parse:
                    try:
                        data_list.append(case_dict[case_name])
                    except KeyError as ex:
                        print('{}测试用例名称错误,请检查拼写、大小写.'.format(case_name))
                        raise ex
            else:
                # Loop through the configuration data under the node, 
                # so case begins the use case
                for key in case_dict:
                    # What begins with a case in configuration data is considered a use case.
                    if str(key).lower().startswith('case'):

                        # Organize DDT [] data, and each case is a dict object
                        data_list.append(case_dict[key])
        else:
            raise Exception("The CASE execution queue is empty.")
        # csv parameter
        temp_list = _csv_parameter_func(case_path, data_list, temp_list)

    # case order by desc
    data_list = sorted_data_fuction(temp_list, orderby='desc')
    return data_list


def _csv_parameter_func(case_path, data_list, temp_list):
    """
    CSV Paraetems data.

    Args:
        case_path: d:\\xxxx.yaml
        data_list: Read yaml
        temp_list: Temporarily store parameterized data.

    Example:
        temp_list = _csv_parameter_func(case_path, data_list, temp_list)

    Return:
        temp_list
    """
    try:
        # csv参数化数据
        for i_list in data_list:
            if 'CSV_VAR' in str(i_list[0].keys()).upper():
                # 字段应该加错误处理...
                csv_path = str(i_list[0]['CSV_VAR']['file_path'])

                # 处理相对路径
                if not os.path.isabs(csv_path):
                    csv_path = os.path.join(case_path, csv_path)

                # 读取csv并加以处理
                csv_list = csv_readline_to_list(csv_path)
                parse_data_list = csv_data_ext(i_list, csv_list)
                temp_list.extend(parse_data_list)
            else:
                # 无需参数化
                temp_list.append(i_list)
    except KeyError as ex:
        raise Exception(ex)

    return temp_list


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


def read_file(filepath, mode):
    """
    The write file.

    Args:
        filepath: File absolute path.
        mode: Read and Write.
        txt: text content.

    Usage:
        read_file('/xxxx/temp.txt', 'r')

    Return:
        There is no.
    """
    with io.open(filepath, mode, encoding='utf-8') as fp:
        content = fp.read()
    return content


def remove_file(file):
    """
    The remove file.

    Args:
        file: file absoule path.

    Exaplam:
        file = "xxxx.txt"
        remove_file(file)
    Return:
        There is no return.
    """
    if os.path.exists(file):
        os.remove(file)

def get_ip_addr():
    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.

    Usage:
        import socket
        ip_addr = get_ip_addr()
    Return:
        ip Address.
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def get_ip_or_name():
    """
    To obtain the local computer name or IP address.

    Args:

    Usage:
        import socket
        addr, name = get_ip_or_name()

    Return:
        IP address, Computer name.
    """
    # Access to the local computer name.
    name = socket.getfqdn(socket.gethostname())
    # Access to the local computer address.
    addr = socket.gethostbyname(name)

    return addr, name


def print_font_color(msg, color='WHITE'):
    """
    Print console font color.

    Args:
        msg: Print message content.
        color: Set the font to color; The default is white.
               BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
    Usage:
        from colorama import Fore
        msg = 'font color.'
        print_font_color(msg, 'red')

        Set the font to red.
    Return:
        There is no return.
    """
    color = getattr(Fore, color.upper())
    print(color, msg.strip(), Style.RESET_ALL)


def print_backgroup_color(msg, color='WHITE'):
    """
    Print console backgroup color.

    Args:
        msg: Print message content.
        color: Set the font to backgroup color; The default is white.
               BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
    Usage:
        from colorama import Back
        msg = 'font backgroup color.'
        print_backgroup_color(msg, 'red')

        Set the font to backgroup is red.
    Return:
        There is no return.
    """
    color = getattr(Back, color.upper())
    print(color, str(msg).strip(), Style.RESET_ALL)


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
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream=stream, Dumper=OrderedDumper, allow_unicode=True)


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_yaml_load(yaml_path, Loader=yaml.Loader, object_pairs_hook=collections.OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    with io.open(yaml_path, 'r', encoding='utf-8') as fp:
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
        ordered_dump(data, fp, Dumper=yaml.SafeDumper,
            allow_unicode=True, default_flow_style=False, indent=4)


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
        content_dict = collections.OrderedDict()
        content_dict['Desc'] = '接口中文名称/api/demo'
        content_dict['Url'] = "https:/test.it/api/demo"
        content_dict['Method'] = "POST"
        content_dict['Headers'] = {"content-type": "application/json;charset=UTF-8"}
        content_dict['Data'] = data
        content_dict['OutPara'] = ""
        content_dict['Assert'] = []
        # case template.
        tmpl = {
            "TEST_CASE": {
                "Case1": [
                    {'Desc': '接口用例详细中文描述'},
                    content_dict
                ]
            }
        }
    else:
        tmpl = data
    # Write case to YAML file.
    write_case_to_yaml(fileyaml, tmpl)
    print("Conversion to complete.")


def parse_output_parameters(params):
    """
    Parse the test case output parameters.

    Args:
        params: res[0].tr.id
    Example:
        ret = parse_output_parameters('result.res.data[0].id')
        e.g. Data.tr.id => Data['tr']['id']
             res.tr.id => res['tr]['id]
             res[0].tr.id => res[0]['tr']['id']
             cookie.SESSION => cookie['SESSION']
             headers.Content-Type => headers['Content-Type']
    """
    param_list = params.split(".")

    # Interception object.
    param_obj = param_list[0]
    param_list.pop(0)

    # Template string.
    template = "['{}']"
    parse_string = ''
    # Parse the test case output parameters.
    for args in param_list:
        if "[" in args:
            left_string = ''
            for num, val in enumerate(args.split("[")):
                if num == 0:
                    val = "['{}']".format(val)
                left_string = left_string + val + "["
            left_string = (left_string[:-1])
            parse_string = parse_string + left_string
        else:
            parse_string = parse_string + template.format(args)
    ret_string = param_obj + parse_string
    return ret_string


def update_yam_content(conf_file, conf_field, text):
    """
    Update YAML content.

    Args:
        conf_field:
            e.g.
            EMAIL.Smtp_Server => content['EMAIL']['Smtp_Server]
        text:
            YAML content.
    Example:
        from ruamel import yaml as yam
        import io

        update_yam_content("EMAIL.Smtp_Server", "smtp.mail.net")
    Return:
        There is no return.
    """
    from ruamel import yaml as yam
    parse_conf = parse_output_parameters('content.{}'.format(conf_field))
    with io.open(conf_file, 'r', encoding='utf-8') as fp:
        content = yam.load(fp, Loader=yam.RoundTripLoader)
        try:
            exec(parse_conf)
            exec('{} = text'.format(parse_conf))
        except KeyError as ex:
            print('[KeyError]:{}'.format(ex))

    with io.open(conf_file, 'w', encoding='utf-8') as fw:
        yam.dump(content, stream=fw, Dumper=yam.RoundTripDumper, allow_unicode=True)


def update_yam_content_2(conf_field, text):
    """
    Update YAML content.

    Args:
        conf_field:
            e.g.
            EMAIL.Smtp_Server => content['EMAIL']['Smtp_Server]
        text:
            YAML content.
    Example:
        from ruamel import yaml
        import io

        update_yam_content("EMAIL.Smtp_Server", "smtp.mail.net")
    Return:
        There is no return.
    """
    parse_conf = parse_output_parameters('content.{}'.format(conf_field))
    with io.open('config.yaml', 'r', encoding='utf-8') as fp:
        # usage example:
        content = ordered_load(fp, yaml.SafeLoader)
        exec('{} = text'.format(parse_conf))
        print(content)
    with io.open('config.yaml', 'w', encoding='utf-8') as fw:
        # usage:
        ordered_dump(content, stream=fw, Dumper=yaml.SafeDumper)


def csv_readline_to_list(csv_file):
    """
    Read the CSV content by line.

    Example:
        csv content:
            |name|age|
            | a  |21 |
            | b  |22 |
            | c  |23 |
            | d  |24 |
            | e  |25 |
        ret = csv_readline_to_list("d/demo.csv")
    Return:
        [['name', 'age'], ['a', '21'], ['b', '22'], ['c', '34'], ['d', '24'], ['e', '25']] 
    """
    try:
        with open(csv_file, 'r', encoding="utf-8") as csv_fp:
            reader = csv.reader(csv_fp)
            rows = [row for row in reader]
    except UnicodeDecodeError:
        with open(csv_file, 'r', encoding="gbk") as csv_fp:
            reader = csv.reader(csv_fp)
            rows = [row for row in reader]

    except IOError as ex:
        raise Exception(ex)

    return rows


def csv_data_ext(d_dict, csv_list):
    """
    Args:
        d_dict:
            'Data': {'req': {'begin_time': '${name}$', 'end_time': '${age}$', 'shop_id': 1512995661}, 'appid': '${name}$', 'sig': "%{sign({'data': 'data.req', 'appid':'data.appid', 'ts':'data.ts', 'v': 'data.v','appkey':'${appkey}$'})}%", 'v': 2.0, 'ts': 1564967996}
        csv_list:
            [['name', 'age'], ['a', '21'], ['b', '22'], ['c', '23'], ['d', '24']]
    Return:
        [
            'Data': {'req': {'begin_time': 'a', 'end_time': '21', 'shop_id': 1512995661}, 'appid': '${name}$', 'sig': "%{sign({'data': 'data.req', 'appid':'data.appid', 'ts':'data.ts', 'v': 'data.v','appkey':'${appkey}$'})}%", 'v': 2.0, 'ts': 1564967996},
            'Data': {'req': {'begin_time': 'b', 'end_time': '22', 'shop_id': 1512995661}, 'appid': '${name}$', 'sig': "%{sign({'data': 'data.req', 'appid':'data.appid', 'ts':'data.ts', 'v': 'data.v','appkey':'${appkey}$'})}%", 'v': 2.0, 'ts': 1564967996},
            'Data': {'req': {'begin_time': 'c', 'end_time': '23', 'shop_id': 1512995661}, 'appid': '${name}$', 'sig': "%{sign({'data': 'data.req', 'appid':'data.appid', 'ts':'data.ts', 'v': 'data.v','appkey':'${appkey}$'})}%", 'v': 2.0, 'ts': 1564967996},
            'Data': {'req': {'begin_time': 'd', 'end_time': '24', 'shop_id': 1512995661}, 'appid': '${name}$', 'sig': "%{sign({'data': 'data.req', 'appid':'data.appid', 'ts':'data.ts', 'v': 'data.v','appkey':'${appkey}$'})}%", 'v': 2.0, 'ts': 1564967996},
        ]
    """
    ext_data = []

    # csv columns name
    columns_list = csv_list[0]
    for j in range(1, len(csv_list)):
        data_repr = repr(d_dict)
        for i, col_name in enumerate(columns_list):

            var_name = '${%s}$' % col_name
            if var_name in data_repr:
                # csv中list or dict转换
                data_repr, csv_list[j][i] = _csv_lst_convert(
                    data_repr,
                    csv_list[j][i],
                    var_name
                    )

                data_repr = data_repr.replace(var_name, csv_list[j][i])
        ext_data.append(list(eval(data_repr)))

    if not ext_data:
        ext_data = d_dict
    return ext_data


def _csv_lst_convert(data_repr, csv_lst, var_name):
    """
    csv convert  list or dict
    """
    # csv中list or dict转换
    try:
        col_val = csv_lst.strip()
        if col_val != '':
            tmp_eval = eval(csv_lst)
            if isinstance(tmp_eval, list) or isinstance(tmp_eval, dict):
                data_repr = data_repr.replace(
                    '"{}"'.format(var_name), var_name
                    ).replace(
                    "'{}'".format(var_name), var_name
                )
            else:
                # list or dict to string
                if col_val[:1] == "'" or col_val[:1] == '"':
                    csv_lst = col_val[1:len(col_val)-1]
    except NameError:
        pass

    return data_repr, csv_lst
