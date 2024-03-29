import time
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from httptesting.library.config import conf
from httptesting.library import gl


class EmailClass(object):
    def __init__(self):
        self.curDateTime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))  # 当前日期时间
        self.config = conf.get_yaml_field(gl.configFile)  # 配置文件路径
        self.sender = self.config['EMAIL']['Smtp_Sender']  # 从配置文件获取，发件人
        self.receivers = self.config['EMAIL']['Receivers']   # 从配置文件获取，接收人
        self.msg_title = self.config['EMAIL']['Msg_Title']  # 从配置文件获取，邮件标题
        self.sender_server = self.config['EMAIL']['Smtp_Server']  # 从配置文件获取，发送服务器
        self.From = self.config['EMAIL']['From']
        self.To = self.config['EMAIL']['To']
        self.Port = self.config['EMAIL']['Port']
    '''
    配置邮件内容
    '''
    def set_mail_content(self, html_path):
        print(self.receivers)
        msg = MIMEMultipart()
        msg['From'] = Header(self.From, 'utf-8')
        msg['To'] = self.To
        msg['Subject'] = Header('%s%s' % (self.msg_title, self.curDateTime), 'utf-8')

        # #两个附件路径
        file = html_path

        # 增加邮件内容为html
        fp = open(file, 'rb')
        html = fp.read()
        msg.attach(MIMEText(str(html), 'html', 'utf-8'))
        fp.close()

        # 增加附件
        html = self.add_attach(file, filename='Report%s.html' % self.curDateTime)  # 自动化测试报告附件

        msg.attach(html)

        return msg

    '''
    增加附件
    '''
    @staticmethod
    def add_attach(path, filename='Report.html'):
        attach = MIMEBase('application', 'octet-stream')
        with open(path, 'rb') as fp:

            attach.set_payload(fp.read())
            attach.add_header('Content-Disposition', 'attachment', filename=filename)
            encoders.encode_base64(attach)

        return attach

    '''
    发送电子邮件
    '''
    def send_email(self, message):
        try:
            smtp = smtplib.SMTP_SSL(self.sender_server, self.Port)

            smtp.connect(self.sender_server)
            smtp.login(self.sender, self.config['EMAIL']['Password'])
            smtp.sendmail(self.sender, self.receivers, message.as_string())
            smtp.quit()
            print("邮件发送成功")
        except smtplib.SMTPException as ex:
            print("Error: 无法发送邮件.%s" % ex)

    # 发送调用
    def send(self, file_path):
        self.send_email(self.set_mail_content(file_path))


if __name__ == "__main__":
    EmailClass().send('')
