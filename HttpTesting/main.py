import unittest
import shutil
import os,time,json,io
import logging
from HttpTesting.globalVar import gl
from HttpTesting.library import HTMLTESTRunnerCN
from HttpTesting.library import scripts
from HttpTesting.library.scripts import (get_yaml_field, start_web_service, write_file)
from HttpTesting.library.emailstmp import EmailClass
from HttpTesting.library.case_queue import case_exec_queue
from HttpTesting import case
from HttpTesting.library.falsework import create_falsework
from HttpTesting.library.har import ConvertHarToYAML
import argparse

########################################################################
#Command line mode.
def run_min():

    #Takes the current path of the command line
    cur_dir= os.getcwd()
    os.chdir(cur_dir)

    parse = argparse.ArgumentParser(description='HttpTesting parameters')

    parse.add_argument(
        "-file", 
        default='', 
        help='The file path; File absolute or relative path.'
        )
    parse.add_argument(
        "-dir", 
        default='',
        help='The folder path; folder absolute or relative path.'
        )
    parse.add_argument(
        "-startproject", 
        default='',
        help='Generate test case templates.'
        )
    parse.add_argument(
        "-config", 
        default='',
        help='Basic setting of framework.'
        )
    parse.add_argument(
        "-har", 
        default='',
        help='Convert the har files to YAML. har file is *.har'
        )
    parse.add_argument(
        "-convert", 
        default='',
        help='Convert the har files to YAML. YAML file is *.yaml'
        )



    args = parse.parse_args()
    case_file = args.file
    case_dir = args.dir
    start_project = args.startproject
    config = args.config
    har = args.har
    vert = args.convert

    # Conver YAML.
    if vert != '':
        yamlfile = os.path.join(cur_dir, str(vert).strip())
        scripts.generate_case_tmpl(yamlfile)


    #Convert har files to YAML.
    #r'D:\httphar.har'
    if har != '':
        temp_dict = ConvertHarToYAML.convert_har_to_ht(har)
        ConvertHarToYAML.write_case_to_yaml('', temp_dict)

    #Setting global var.
    if config == 'set':
        try:
            os.system(gl.configFile)
        except (KeyboardInterrupt, SystemExit):
            print("已终止执行.")

    if start_project !='':
        create_falsework(os.path.join(os.getcwd(), start_project))

    tempList = []
    #Get the yaml file name and write to the queue.
    if case_file != '':
        # case_exec_queue.put(case_file)
        tempList.append(os.path.join(cur_dir, case_file))
        write_file(os.path.join(gl.loadcasePath, 'temp.txt'), 'w', ';'.join(tempList))
        #Began to call.
        Run_Test_Case.invoke()


    if case_dir != '':
        for root, dirs, files in os.walk(case_dir):
            for f in files:
                if 'yaml' in f:
                    # case_exec_queue.put(os.path.join(case_dir, f))
                    d = os.path.join(cur_dir, case_dir)
                    tempList.append(os.path.join(d, f))

        # Write file absolute path to file. 
        write_file(os.path.join(gl.loadcasePath, 'temp.txt'), 'w', ';'.join(tempList))
        #Began to call.
        Run_Test_Case.invoke()



#########################################################################
# Not in command mode --dir defaults to the testcase directory.
# Example:
# python3 main.py --dir=r"D:\test_project\project\cloud_fi_v2\testcase"
#########################################################################

class Run_Test_Case(object):

    @classmethod
    def create_report_file(cls):
        #测试报告文件名
        report_dir = time.strftime('%Y%m%d_%H%M%S', time.localtime())

        rdir = os.path.join(os.getcwd() ,'report')

        cls.file_name = 'report.html'
        portdir = os.path.join(rdir, report_dir)

        #按日期创建测试报告文件夹
        if not os.path.exists(portdir):
            # os.mkdir(portdir)
            os.makedirs(portdir)

        cls.filePath = os.path.join(portdir, cls.file_name)  # 确定生成报告的路径

        return cls.filePath


    @staticmethod
    def copy_custom_function():
        #自定义函数功能
        func = os.path.join(os.getcwd(), 'extfunc.py')
        target = os.path.join(gl.loadcasePath, 'extfunc.py')

        if os.path.exists(func):
            shutil.copy(func, target)   


    @staticmethod
    def tmpl_msg(low_path, file_name):
        # 发送钉钉模版测试结果
        config = get_yaml_field(gl.configFile)
        #report外网发布地址ip+port
        report_url = config['REPORT_URL']
        #钉钉标题
        content = config['DING_TITLE']
        # 发送钉钉消息
        msg = """{}已完成:\n测试报告地址:{}/{}/{}"""
        msg = msg.format(content, report_url, low_path, file_name)

        return msg

    @staticmethod
    def run(filePath):
        """
        Execute the test and generate the test report file.
        :param filePath: Report file absolute path.
        :return: There is no.
        """
        config  = get_yaml_field(gl.configFile)
        exe_con = config['ENABLE_EXECUTION']
        exe_num = config['EXECUTION_NUM']
        rerun = config['ENABLE_RERUN']
        renum = config['RERUN_NUM']  
        repeat = config['ENABLE_REPEAT']
        repeat_num = config['REPEAT_NUM']
        exec_mode = config['ENABLE_EXEC_MODE']


        #custom function
        Run_Test_Case.copy_custom_function()

        #Enable repeat case.
        peatargs = ''
        if repeat:
            peatargs = ' --count={} '.format(repeat_num)


        #Enable CPU concurrency
        pyargs = ''  
        if exe_con:
            pyargs = ' -n {} '.format(exe_num)

        #Enable failed retry
        reargs = ''
        if rerun:
            reargs = ' --reruns {} '.format(renum)

        #Load the pytest framework, which must be written here or DDT will be loaded first.
        # from HttpTesting.case import test_load_case
        casePath = gl.loadcasePath
        
        #Output mode console or report.
        if exec_mode:
            cmd = 'cd {} && py.test -q -s --tb=no {}'.format(casePath, 'test_load_case.py')
        else:
            cmd = 'cd {} && py.test {} {} {} {} --html={} --tb=no --self-contained-html'.format(
                casePath, 
                pyargs,
                reargs,
                'test_load_case.py', 
                peatargs,
                filePath
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
        ##########################Read configuration information###############
        config  = get_yaml_field(gl.configFile)
        dd_enable = config['ENABLE_DDING']
        dd_token = config['DD_TOKEN']
        dd_url = config['DING_URL']
        email_enable = config['EMAIL_ENABLE']
        ########################################################################

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


# if __name__=="__main__":
#     run_min()

