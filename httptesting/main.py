# ########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.insert(0, rootPath)
# ########################################################
import os
import shutil
import time
from httptesting.library import gl
from httptesting.library import scripts
from httptesting.library.scripts import (get_yaml_field,
                                         write_file,
                                         read_file,
                                         remove_file
                                         )
from httptesting.library.emailstmp import EmailClass
from httptesting.library.falsework import create_falsework
from httptesting.library.har import ConvertHarToYAML
from httptesting import __version__
import argparse

########################################################################
"""
Command line mode.
"""


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

    # Conver YAML.
    if vert:
        yamlfile = os.path.join(cur_dir, str(vert).strip())
        scripts.generate_case_tmpl(yamlfile)

    # Convert har files to YAML.
    if har:
        temp_dict = ConvertHarToYAML.convert_har_to_ht(har)
        ConvertHarToYAML.write_case_to_yaml('', temp_dict)

    # Setting global var.
    if config == 'set':
        try:
            os.system(gl.configFile)
        except (KeyboardInterrupt, SystemExit):
            print("已终止执行.")

    if start_project:
        create_falsework(os.path.join(os.getcwd(), start_project))

    temp_list = []
    # Get the yaml file name and write to the queue.
    if case_file:
        # Specify the execution CASE.
        fargs = '&#'.join(case_file)
        temp_list.append(os.path.join(cur_dir, fargs))

        write_file(
            os.path.join(gl.loadcasePath, 'temp.txt'),
            'w',
            ';'.join(temp_list)
        )
        # Began to call.
        Run_Test_Case.invoke()

    if case_dir:
        for root, dirs, files in os.walk(case_dir):
            for f in files:
                if 'yaml' in f:
                    d = os.path.join(cur_dir, case_dir)
                    temp_list.append(os.path.join(d, f))

        # Write file absolute path to file.
        write_file(
            os.path.join(gl.loadcasePath, 'temp.txt'),
            'w',
            ';'.join(temp_list)
        )
        # Began to call.
        Run_Test_Case.invoke()

#########################################################################
# Not in command mode --dir defaults to the testcase directory.
# Example:
# python3 main.py --dir=r"D:\test_project\project\cloud_fi_v2\testcase"
#########################################################################


class Run_Test_Case(object):

    @classmethod
    def create_report_file(cls):
        # 测试报告文件名
        report_dir = time.strftime('%Y%m%d_%H%M%S', time.localtime())

        rdir = os.path.join(os.getcwd(), 'report')

        cls.file_name = 'report.html'
        portdir = os.path.join(rdir, report_dir)

        # 按日期创建测试报告文件夹
        if not os.path.exists(portdir):
            # os.mkdir(portdir)
            os.makedirs(portdir)
        # 确定生成报告的路径
        cls.filePath = os.path.join(portdir, cls.file_name)  

        return cls.filePath

    @staticmethod
    def copy_custom_function():
        # 自定义函数功能
        func = os.path.join(os.getcwd(), 'extfunc.py')
        target = os.path.join(gl.loadcasePath, 'extfunc.py')

        if os.path.exists(func):
            shutil.copy(func, target)  

    @staticmethod
    def tmpl_msg(low_path, file_name):
        # 发送钉钉模版测试结果
        config = get_yaml_field(gl.configFile)
        # report外网发布地址ip+port
        report_url = config['REPORT_URL']
        # 钉钉标题
        content = config['DING_TITLE']
        # 从报告中取得测试结果数据 e.g. 3 tests; 2.23 seconds; 3 passed; 0 failed; 0 errors
        file_result = os.path.join(gl.loadcasePath, 'result.txt')
        #
        result_content = read_file(file_result, 'r')
        # Remove file
        remove_file(file_result)

        res_list = result_content.split(";")

        # 发送钉钉消息
        msg = """{}执行【已完成】:\n共{}个用例, 执行耗时{}秒, 通过{}, 失败{}, 错误{}, 通过率{}\n测试报告: {}/{}"""
        msg = msg.format(
            content,
            res_list[0],
            res_list[1],
            res_list[2],
            res_list[3],
            res_list[4],
            res_list[5],
            report_url,
            low_path
            )

        return msg

    @staticmethod
    def run(filePath):
        """
        Execute the test and generate the test report file.
        Args:
            fileath: Report file absolute path.
        Return:
            There is no return.
        """
        config = get_yaml_field(gl.configFile)
        exe_con = config['ENABLE_EXECUTION']
        exe_num = config['EXECUTION_NUM']
        rerun = config['ENABLE_RERUN']
        renum = config['RERUN_NUM']  
        repeat = config['ENABLE_REPEAT']
        repeat_num = config['REPEAT_NUM']
        exec_mode = config['ENABLE_EXEC_MODE']
        debug_mode = config['ENABLE_DEBUG_MODE']

        # custom function
        Run_Test_Case.copy_custom_function()

        # Enable repeat case.
        peatargs = ''
        if repeat:
            peatargs = ' --count={} '.format(repeat_num)

        # Enable CPU concurrency
        pyargs = ''
        if exe_con:
            pyargs = ' -n {} '.format(exe_num)

        # Enable failed retry
        reargs = ''
        if rerun:
            reargs = ' --reruns {} '.format(renum)

        # debug mode print debug info.
        if not debug_mode:
            debug = '--tb=no'
        else:
            debug = ''

        """
        Load the pytest framework,
        which must be written here or DDT will be loaded first.
        from httptesting.case import test_load_case
        """
        case_path = gl.loadcasePath
        # Output mode console or report.
        if exec_mode:
            cmd = 'cd {} && py.test -q -s {} {} {} {}'.format(
                case_path,
                reargs,
                'test_load_case.py',
                peatargs,
                debug
            ) 
        else:
            cmd = 'cd {} && py.test {} {} {} {} --html={} {} --self-contained-html'.format(
                case_path,
                pyargs,
                reargs,
                'test_load_case.py',
                peatargs,
                filePath,
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
        config = get_yaml_field(gl.configFile)
        dd_enable = config['ENABLE_DDING']
        dd_token = config['DD_TOKEN']
        dd_url = config['DING_URL']
        email_enable = config['EMAIL_ENABLE']
        # END CONFIG.

        # Test report file name.
        time_str = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        filePath = Run_Test_Case.create_report_file()

        # Start test the send pin message.
        if dd_enable:
            scripts.send_msg_dding(
                '{}:★开始API接口自动化测试★'.format(time_str),
                dd_token,
                dd_url
            )

        # Execute the test and send the test report.
        Run_Test_Case.run(filePath)
        if dd_enable:
            # Template message.
            dir_list = filePath.split('\\')
            low_path = dir_list[len(dir_list) - 2]
            msg = Run_Test_Case.tmpl_msg(low_path, Run_Test_Case.file_name)
            print(msg)
            scripts.send_msg_dding(msg, dd_token, dd_url)

        if email_enable:
            # Send test report to EMAIL.
            email = EmailClass()
            email.send(filePath)


if __name__ == "__main__":
    run_min()
