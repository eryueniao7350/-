"""
邮件发送模块
Email sending module using SMTP.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def send_email(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    recipient_email: str,
    subject: str,
    text_content: str,
    html_content: str,
) -> bool:
    """
    通过 SMTP 发送邮件

    Args:
        smtp_server: SMTP 服务器地址
        smtp_port: SMTP 端口号
        sender_email: 发件人邮箱
        sender_password: 发件人密码或应用专用密码
        recipient_email: 收件人邮箱
        subject: 邮件主题
        text_content: 纯文本内容（备用）
        html_content: HTML 内容

    Returns:
        是否发送成功
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email

        # 添加纯文本和 HTML 两种格式
        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        logger.info("Email sent successfully to %s", recipient_email)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.exception("SMTP authentication failed. Check credentials.")
        return False
    except smtplib.SMTPException:
        logger.exception("SMTP error occurred while sending email.")
        return False
    except Exception:
        logger.exception("Unexpected error sending email.")
        return False
