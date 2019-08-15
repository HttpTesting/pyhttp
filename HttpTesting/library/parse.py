import re
from HttpTesting.library.func import *


def parse_param_variables(data):
    """
    """
    var_regx_compile = re.compile(r"\${(.*?)}")

    take_list = var_regx_compile.findall(str(data))

    return take_list


def parse_args_func(func_class, data):
    """
    Parse the function variables in the data.

    Args:
        func_class: FUNC  class object.
        data: string.

    Example:
        import re
        from HttpTesting.library.func import *
        >>> parse_args_func(FUNC, 'md5:%{md5("123")}; timestamp:%{timestamp()}')
        md5:202cb962ac59075b964b07152d234b70; timestamp:1565840163

    Return:
        Replacement data.
    """
    func_regx_compile = re.compile(r"%{(.*?)}%")

    take = func_regx_compile.findall(str(data))

    for val in take:
        func = '{}.{}'.format(func_class.__name__, val)

        ret_func = eval_string_parse(func)
        if isinstance(ret_func, str):

            list_string = ['%{' + val + '}%', "'%{" + val + "}%'", '"%{' + val + '}%"']
            data = replace_list_batch_string(data, list_string, ret_func)
        else:

            list_string = ["'%{" + val + "}%'", '"%{' + val + '}%"', '%{' + val + '}%']
            data = replace_list_batch_string(data, list_string, ret_func)

    return eval_string_parse(data)


def replace_list_batch_string(string, list_string, new):
    """
    Batch replace value in string.

    Args:
        string： The original string。
            e.g.'md5:%{md5("123")}; timestamp:%{timestamp()}'
        list_string: ["%{md5("123")}", '"%{md5(\"123\")}"', '%{md5("123")}']
        new: 202cb962ac59075b964b07152d234b70

    Example:
        >>> val = "%{md5('123')"
        >>> list_string = ["'%{" + val + "}'", '"%{' + val + '}"', '%{' + val + '}']
        >>> data = replace_list_batch_string(data, list_string, ret_func)
    Return:
        string: Replaced string
    """
    for old in list_string:
        string = string.__str__().replace(old.__str__(), new.__str__())
    return string


def eval_string_parse(string):
    """
    Parse the string to native.

    Args:
        string: A string to be parsed.
    Example:
        >>> eval_string_parse("123")
        123 <class 'int'>

        >>> eval_string_parse("12.3")
        12.3 <class 'float'>

        >>> eval_string_parse("{'name': 'yhleng', 'age': 27}")
        {'name': 'yhleng', 'age': 27}  <class 'dict'>

        >>> eval_string_parse("[1,2,3,4,5]")
        [1,2,3,4,5] <class 'list'>
    Return:
        String prototype.
    """
    try:
        ret = eval(string)
    except (TypeError, ValueError, NameError, SyntaxError):
        ret = string
    return ret


def parse_string_value(str_value):
    """ 
    Parse string, restore type.

    Example:
        >>> parse_string_value("123") 
        123 <class 'int'>

        >>> parse_string_value("12.3") 
        12.3 <class 'float'>

        >>> parse_string_value("abc") 
        abc <class 'str'>
    """
    try:
        return eval_string_parse(str_value)
    except (ValueError, SyntaxError):
        return str_value



if __name__ == "__main__":
    data = {
        "md5": '%{md5("123")}',
        "timestamp": "${var}"
    }
    # ret = parse_args_func(FUNC, data)
    # print(ret)
    ret = parse_param_variables("aaaa${var}bbbb${okay}")
    print(ret)
