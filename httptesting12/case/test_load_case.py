import os
import pytest
from httptesting.library.scripts import load_case_data
from httptesting.library.case import exec_test_case
from httptesting.globalVar import gl

# ###################################################################################
# 单个文件Debug时启用
from httptesting.library.case_queue import case_exec_queue
# case_exec_queue.put(os.path.join(gl.testCasePath, "POS_INFO.yaml"))
with open(os.path.join(gl.loadcasePath, 'temp.txt'), 'r', encoding='utf-8') as fp:
    content = fp.read()
    clist = content.split(';')
    for abspath in clist:
        case_exec_queue.put(abspath)
#####################################################################################


class TestCaseExecution(object):
    """
    Use the python pytest framework.
    """
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    param_list = load_case_data()

    @pytest.fixture(scope='session', params=param_list)
    def data(self, request):
        """
        fixture parameters.
        """
        return request.param

    def testcase(self, data):
        self.testcase.__func__.__doc__ = data[0]['Desc']

        # Execution the YAML test case.
        exec_test_case(data)
