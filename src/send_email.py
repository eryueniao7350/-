"""
邮件发送模块
Sends oil market report via email using SMTP.
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def send_email(
    subject: str,
    plain_body: str,
    html_body: str,
    to_email: str | None = None,
) -> bool:
    """
    通过 SMTP 发送邮件

    所需环境变量:
        SMTP_SERVER:   SMTP 服务器地址 (如 smtp.gmail.com)
        SMTP_PORT:     SMTP 端口号 (如 587)
        SMTP_USERNAME: SMTP 登录用户名
        SMTP_PASSWORD: SMTP 登录密码 (Gmail 用户请使用应用专用密码)
        TO_EMAIL:      收件人邮箱地址 (也可通过参数传入)
    """
    smtp_server = os.environ.get("SMTP_SERVER", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_username = os.environ.get("SMTP_USERNAME", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    recipient = to_email or os.environ.get("TO_EMAIL", "")

    if not all([smtp_server, smtp_username, smtp_password, recipient]):
        logger.error(
            "Missing required email configuration. "
            "Please set SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, and TO_EMAIL environment variables."
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_username
    msg["To"] = recipient

    # 添加纯文本和 HTML 两种格式，邮件客户端会优先显示 HTML
    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        logger.info("Connecting to SMTP server %s:%d...", smtp_server, smtp_port)
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, [recipient], msg.as_string())
        logger.info("Email sent successfully to %s", recipient)
        return True
    except Exception:
        logger.exception("Failed to send email")
        return False
