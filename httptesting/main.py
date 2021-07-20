# ########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.insert(0, rootPath)
# ########################################################
import shutil
import time
from httptesting.library import gl
from httptesting.library import scripts
from httptesting.library.parse import parse_string_value
from httptesting.library.scripts import (write_file,
                                         read_file,
                                         remove_file,
                                         update_yam_content
                                         )
from httptesting.library.config import conf
from httptesting.library.emailstmp import EmailClass
from httptesting.library.falsework import create_falsework
from httptesting.library.har import ConvertHarToYAML
from httptesting import __version__
import argparse

########################################################################
"""
Command line mode.
"""


def _parse_config(config):
    """
    Parse config parameters.
    """
    if config:
        # Setting global var.
        if config[0] == 'set' and config.__len__() == 1:
            try:
                os.system(gl.configFile)
            except (KeyboardInterrupt, SystemExit):
                print("已终止执行.")
        elif config[0] == 'set' and len(config) == 2 and '=' in config[1]:
            cf = config[1].split("=")
            update_yam_content(gl.configFile, cf[0], parse_string_value(cf[1]))

        elif config[0] == 'get' and len(config) == 2 and '=' not in config[1]:
            content = conf.get_yaml_field(gl.configFile)

            try:
                print(content[config[1]])
            except KeyError as ex:
                print('[KeyError]: {}'.format(ex))
        else:
            print('Unknown command: {}'.format(config[0]))


def _convert_case_to_yaml(vert):
    """
    Convert case to YAML.
    """
    if vert:
        yamlfile = os.path.join(os.getcwd(), str(vert).strip())
        scripts.generate_case_tmpl(yamlfile)


def _convert_httphar_to_yaml(har):
    """
    Convert http.har to YAML.
    """
    if har:
        temp_dict = ConvertHarToYAML.convert_har_to_ht(har)
        ConvertHarToYAML.write_case_to_yaml('', temp_dict)


def _false_work(start_project):
    """
    False work.
    """
    if start_project:
        create_falsework(os.path.join(os.getcwd(), start_project))


def _get_file_yaml(case_file):
    """
    Get file case YAML.
    """
    temp_list = []
    # Get the yaml file name and write to the queue.
    if case_file:
        # Specify the execution CASE.
        fargs = '&#'.join(case_file)
        temp_list.append(os.path.join(os.getcwd(), fargs))
        cache_dir = os.path.join(gl.loadcasePath, ".am_cache")
        write_file(
            os.path.join(cache_dir, 'yaml.cache'),
            'w',
            ';'.join(temp_list)
        )
        return True
    return False


def _get_dirs_case_yaml(case_dir):
    """
    Get dirs case YAML.
    """
    temp_list = []
    if case_dir:
        for root, dirs, files in os.walk(case_dir):
            for f in files:
                if 'yaml' in f:
                    d = os.path.join(os.getcwd(), case_dir)
                    temp_list.append(os.path.join(d, f))
        # 缓存目录
        cache_dir = os.path.join(gl.loadcasePath, ".am_cache")
        # Write file absolute path to file.
        write_file(
            os.path.join(cache_dir, 'yaml.cache'),
            'w',
            ';'.join(temp_list)
        )
        return True
    return False


def run_min():
    """
    Perfrom interface test entry.

    Args: None
    Usage:
        Command line execution.
    Return:
        There is no return.
    """

    # Takes the current path of the command line
    cur_dir = os.getcwd()
    os.chdir(cur_dir)

    parse = argparse.ArgumentParser(
        description='httptesting HTTP(s) interface testing framework.',
        prog='httptesting'
        )
    parse.add_argument(
        "-v",
        "--version",
        action='version',
        version="%(prog)s {}".format(__version__),
        help='Framework version.'
        )
    parse.add_argument(
        "-f",
        "--file",
        nargs='+',
        default='',
        help='The file path; File absolute or relative path.'
        )
    parse.add_argument(
        "-d",
        "--dir",
        default='',
        help='The folder path; folder absolute or relative path.'
        )
    parse.add_argument(
        "-sp",
        "--startproject",
        default='',
        help='Generate test case templates.'
        )
    parse.add_argument(
        "-conf",
        "--config",
        nargs="+",
        default='',
        help='Basic setting of framework.'
        )
    parse.add_argument(
        "-har",
        default='',
        help='Convert the har files to YAML. har file is *.har'
        )
    parse.add_argument(
        "-c",
        "--convert",
        default='',
        help='Convert the har files to YAML. YAML file is *.yaml'
        )

    # Command line arguments are assigned to varibales.
    args = parse.parse_args()
    case_file = args.file
    case_dir = args.dir
    start_project = args.startproject
    config = args.config
    har = args.har
    vert = args.convert

    # convert YAML.
    _convert_case_to_yaml(vert)

    # Convert har files to YAML.
    _convert_httphar_to_yaml(har)

    # Setting global var.
    _parse_config(config)

    # False work.
    _false_work(start_project)

    # Write file absolute path to file.
    # Get the yaml file name and write to the queue.

    _get_file_yaml(case_file)
    _get_dirs_case_yaml(case_dir)
    # Began to call.
    RunTestCase.invoke()


#########################################################################
# Not in command mode --dir defaults to the testcase directory.
# Example:
# python3 main.py --dir=r"D:\test_project\project\cloud_fi_v2\testcase"
#########################################################################


class RunTestCase(object):

    @classmethod
    def create_report_file(cls):
        cls.file_name = 'report.html'
        report_dir = os.path.join(
            os.path.join(os.getcwd(), 'report'),
            time.strftime('%Y%m%d_%H%M%S', time.localtime())
        )

        # 按日期创建测试报告文件夹
        if not os.path.exists(report_dir):
            # os.mkdir(report_dir)
            os.makedirs(report_dir)
        # 确定生成报告的路径
        cls.filePath = os.path.join(report_dir, cls.file_name)

        return cls.filePath

    @staticmethod
    def copy_custom_function():
        # 自定义函数功能
        func = os.path.join(os.getcwd(), 'extfunc.py')
        target = os.path.join(gl.loadcasePath, 'extfunc.py')

        if os.path.exists(func):
            shutil.copy(func, target)

    @staticmethod
    def tmpl_msg(low_path):
        # 发送钉钉模版测试结果
        config = conf.get_yaml_field(gl.configFile)
        # report外网发布地址ip+port
        report_url = config['REPORT_URL']
        # 钉钉标题
        content = config['DING_TITLE']
        # 从报告中取得测试结果数据 e.g. 3 tests; 2.23 seconds; 3 passed; 0 failed; 0 errors
        file_result = os.path.join(gl.loadcasePath, 'result.cache')
        #
        result_content = read_file(file_result, 'r')
        # Remove file
        remove_file(file_result)

        res_list = result_content.split(";")

        # 发送钉钉消息
        msg = """{}执行【已完成】:\n共{}个用例, 执行耗时{}秒, 通过{}, 失败{}, 错误{}, 通过率{}\n测试报告: {}/{}"""
        msg = msg.format(content, res_list[0], res_list[1],
                         res_list[2], res_list[3], res_list[4],
                         res_list[5], report_url, low_path)
        return msg

    @staticmethod
    def run(path):
        """
        Execute the test and generate the test report file.
        Args:
            path: Report file absolute path.
        Return:
            There is no return.
        """
        config = conf.get_yaml_field(gl.configFile)
        exe_con = config['ENABLE_EXECUTION']
        exe_num = config['EXECUTION_NUM']
        rerun = config['ENABLE_RERUN']
        reruns_nums = config['RERUN_NUM']
        repeat = config['ENABLE_REPEAT']
        repeat_num = config['REPEAT_NUM']
        exec_mode = config['ENABLE_EXEC_MODE']
        debug_mode = config['ENABLE_DEBUG_MODE']
        last_failed = config['ENABLE_LAST_FAILED']
        failed_first = config['ENABLE_FAILED_FIRST']

        # custom function
        RunTestCase.copy_custom_function()

        # failed first
        failed_first_args = (' --ff ' if failed_first else '') if not last_failed else ''

        # last failed
        last_failed_args = (' --lf ' if last_failed else '') if not failed_first else ''

        # Enable repeat case.
        repeat_args = ' --count={} '.format(repeat_num) if repeat else ''

        # Enable CPU concurrency
        py_args = ' -n {} '.format(exe_num) if exe_con else ''

        # Enable failed retry
        reruns_args = ' --reruns {} '.format(reruns_nums) if rerun else ''

        # debug mode print debug info.
        debug = '' if debug_mode else '--tb=no'

        """
        Load the pytest framework,
        which must be written here or DDT will be loaded first.
        from httptesting.case import test_load_case
        """
        case_path = gl.loadcasePath
        # Output mode console or report.
        if exec_mode:
            cmd = 'cd {} && py.test -q -s {} {} {} {}'.format(
                case_path, reruns_args, 'test_load_case.py',
                repeat_args, debug
            )
        else:
            cmd = 'cd {} && py.test {} {} {} {} {} {} --html={} {} --self-contained-html'.format(
                case_path,
                py_args,
                reruns_args,
                last_failed_args,
                failed_first_args,
                'test_load_case.py',
                repeat_args,
                path,
                debug
            )
        try:
            os.system(cmd)
        except (KeyboardInterrupt, SystemExit):
            print('已终止执行.')

    @staticmethod
    def invoke():
        """
        Start executing tests generate test reports.
        :return: There is no.
        """
        # CONFIG: Read configuration information
        config = conf.get_yaml_field(gl.configFile)
        dd_enable = config['ENABLE_DDING']
        dd_token = config['DD_TOKEN']
        dd_url = config['DING_URL']
        email_enable = config['EMAIL_ENABLE']
        # END CONFIG.

        # Test report file name.
        time_str = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        path = RunTestCase.create_report_file()

        # Start test the send pin message.
        if dd_enable:
            scripts.send_msg_dding(
                '{}:★开始API接口自动化测试★'.format(time_str),
                dd_token,
                dd_url
            )

        # Execute the test and send the test report.
        RunTestCase.run(path)
        if dd_enable:
            # Template message.
            dir_list = path.split('\\')
            low_path = dir_list[len(dir_list) - 2]
            msg = RunTestCase.tmpl_msg(low_path)
            print(msg)
            scripts.send_msg_dding(msg, dd_token, dd_url)

        if email_enable:
            # Send test report to EMAIL.
            email = EmailClass()
            email.send(path)


if __name__ == "__main__":
    run_min()
