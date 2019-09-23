import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.insert(0, rootPath)

from httptesting.library import parse
from httptesting.library.func import *
import pytest


"""
Function parameters, parse_output_parameters() 
"""
params = [
    ("data[0].res.result.id", "data[0]['res']['result']['id']"),
    ("result.data.name", "result['data']['name']"),
    ("result.data[0].args", "result['data'][0]['args']"),
    ("Data.data.data[0]", "data['data']['data'][0]"),
    ("data[0].res[1].id[0]", "data[0]['res'][1]['id'][0]")
]


@pytest.mark.parametrize("param, expected", params)
def test_parse_out_param(param, expected):
    ret = parse.parse_output_parameters(param)
    assert ret == expected


"""
Parse function: parse_args_func
"""
params = [
    ("%{timestamp()}%", 10),
    ('%{md5("123")}%', 32),
]
@pytest.mark.parametrize("param, expected", params)
def test_parse_function_args(param, expected):
    ret = parse.parse_args_func(FUNC, param)

    assert len(ret.__str__()) == expected


"""
Parse string type: eval_string_parse()
params: (parameter1, parameter2)
"""
params = [
    ("123", 'int'),
    ("12.3", 'float'),
    ("{'name': 'yhleng', 'age': 27}", 'dict'),
    ("[1,2,3,4,5]", 'list'),
]
@pytest.mark.parametrize("param, expected", params)
def test_parse_eval_string(param, expected):
    ret = parse.eval_string_parse(param)
    assert type(ret).__name__ == expected


"""
Cookie Parse: parse_cookie_string()
Parameters: cookie['seesion'] ==> session=12345
            cookie ==> session=12345; token=7y6t5r4e9i
"""
params = [
    ({"session": "12345", "token": "7y6t5r4e9i"}, "cookie['session']", "session=12345"),
    ({"session": "12345", "token": "7y6t5r4e9i"}, "cookie", "session=12345; token=7y6t5r4e9i"),
]
@pytest.mark.parametrize("param, param2, expected", params)
def test_parse_cookie_info(param, param2, expected):
    ret = parse.parse_cookie_string(param, param2)
    assert ret == expected


"""
Parse parameters variable.
parse_parameters_variables()
"""
params = [
    ([{r"${cno}$": 123456}, {r"${id}$": 8765}], {"Data": {"id": r"${id}$", "cno": r"${cno}$"}}),
]
@pytest.mark.parametrize("queue, data", params)
def test_parse_parameters_var(queue, data):
    ret = parse.parse_parameters_variables(queue, data)
    assert ret['Data']['id'] == str(queue[1][r'${id}$'])
    assert ret['Data']['cno'] == str(queue[0][r'${cno}$'])
