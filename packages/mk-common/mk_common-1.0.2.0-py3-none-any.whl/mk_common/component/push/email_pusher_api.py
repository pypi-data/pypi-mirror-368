import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
import os


def send_email(
        sender_name="系统通知",  # 发件人名称
        sender_email="your_email@example.com",  # 发件邮箱
        password="your_password_or_auth_code",  # 密码/授权码
        receiver_emails=["user1@example.com", "user2@example.com"],  # 收件人列表
        subject="系统通知",  # 邮件主题
        content="这是一封测试邮件",  # 邮件内容
        content_type="plain",  # 内容类型: plain/text 或 html
        attachments=None,  # 附件路径列表
        smtp_server="smtp.example.com",  # SMTP服务器
        smtp_port=465  # SMTP端口 (SSL一般465，TLS用587)
):
    """
    发送电子邮件
    """
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = formataddr((sender_name, sender_email))
    msg['To'] = ", ".join(receiver_emails)
    msg['Subject'] = subject

    # 添加邮件正文
    if content_type == "html":
        msg.attach(MIMEText(content, 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(content, 'plain', 'utf-8'))

    # 添加附件
    if attachments:
        for file_path in attachments:
            if not os.path.isfile(file_path):
                continue

            with open(file_path, 'rb') as f:
                file_data = f.read()

            file_name = os.path.basename(file_path)
            attachment = MIMEApplication(file_data, Name=file_name)
            attachment['Content-Disposition'] = f'attachment; filename="{file_name}"'
            msg.attach(attachment)

    try:
        # 创建SMTP连接 (SSL加密)
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_emails, msg.as_string())
        return True, "邮件发送成功"
    except Exception as e:
        return False, f"邮件发送失败: {str(e)}"


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 邮件配置 (以QQ邮箱为例)
    config = {
        "sender_name": "qmt消息推送",
        "sender_email": "",  # 发送信息邮箱
        "password": "",  # 在邮箱设置中获取SMTP授权码
        "receiver_emails": [""],  # 接受信息邮箱
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465
    }

    # 示例1：发送纯文本邮件
    result, message = send_email(
        **config,
        subject="服务器状态告警",
        content="CPU使用率已达95%！请立即处理！"
    )
    # print(message)
    #
    # # 示例2：发送HTML邮件
    # html_content = """
    # <h1>系统日报</h1>
    # <p>时间：2023-10-01</p>
    # <table border="1">
    #     <tr><th>指标</th><th>状态</th></tr>
    #     <tr><td>CPU</td><td style="color:green">正常</td></tr>
    #     <tr><td>内存</td><td style="color:orange">警告</td></tr>
    # </table>
    # """
    # result, message = send_email(
    #     **config,
    #     subject="系统日报",
    #     content=html_content,
    #     content_type="html"
    # )
    #
    # # 示例3：发送带附件的邮件
    # result, message = send_email(
    #     **config,
    #     subject="月度报告",
    #     content="详见附件中的月度统计报告",
    #     attachments=["/path/to/report.pdf", "/path/to/data.xlsx"]
    # )
