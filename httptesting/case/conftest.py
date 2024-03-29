import pytest
from py._xmlgen import html
from datetime import datetime
import re
import os
from httptesting.library.scripts import (get_ip_addr, write_file)
from httptesting.library import gl

# Pattern result.
result_regx_compile = re.compile("\>(.*?)\<\/span>")
# The case number and when.
count_regx_compile = re.compile(r"<p>(\d+) tests ran in (.*?) seconds. </p>")

"""
Summary部分在此设置
"""
@pytest.mark.optionalhook
def pytest_html_results_summary(prefix, summary, postfix):
    # Get configure content.
    prefix.extend([html.p("测试人: 测试组")])

    # Case number and time.
    case_count = str(summary[0])
    # count[0] The case number
    # count[1] The case when
    count = count_regx_compile.findall(case_count)[0]

    # Passed
    passed_str = str(summary[3])
    passed = result_regx_compile.findall(passed_str)[0].strip()

    # Failed
    failed_str = str(summary[9])
    failed = result_regx_compile.findall(failed_str)[0].strip()

    # Error
    error_str = str(summary[12])
    error = result_regx_compile.findall(error_str)[0].strip()

    #pass rate
    passed = int(passed.replace('passed', '').strip())
    failed = failed.replace('failed', '').strip()
    error = error.replace('errors', '').strip()
    # %
    pass_rate = str("%.2f%%" % (float(passed) / float(count[0]) * 100))
    # 缓存目录
    cache_dir = os.path.join(gl.loadcasePath, ".am_cache")
    # 结果缓存目录
    file_path = os.path.join(cache_dir, 'result.cache')
    result_text = "; ".join([count[0], count[1], str(passed), failed, error, str(pass_rate)])
    write_file(file_path, 'w', result_text)



"""
Environment部分在此设置
"""
def pytest_configure(config):

    config._metadata['测试地址'] = get_ip_addr()
    # Remove fields from the list of environment variables.
    envirList = [
        'Plugins', 'Packages', 'WORKSPACE',
        'JAVA_HOME', 'BUILD_ID', 'BUILD_NUMBER',
        'EXECUTOR_NUMBER', 'GIT_BRANCH', 'GIT_URL',
        'NODE_NAME', 'BUILD_URL'
    ]
    for key in envirList:
        if key in config._metadata.keys():
            config._metadata.pop(key)



"""
Results部分在此设置.
"""
@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Description'))
    cells.insert(2, html.th('Time', class_='sortable time', col='time'))
    # cells.insert(1,html.th("Test_nodeid"))
    cells.pop(3)
    cells.pop()

@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.insert(1, html.td(report.description))
    cells.insert(2, html.td(datetime.now(), class_='col-time'))
    # cells.insert(1,html.td(report.nodeid))
    cells.pop(3)
    cells.pop()

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
    # report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")   #设置编码显示中文