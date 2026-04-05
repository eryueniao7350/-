"""
主程序入口
Main entry point: fetch oil market data and send email report.
"""

import logging
import os
import sys
from datetime import datetime, timezone

from src.email_sender import send_email
from src.oil_market import fetch_oil_prices, format_price_html, format_price_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """获取石油市场数据并发送邮件报告"""

    # 从环境变量读取配置
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_str = os.environ.get("SMTP_PORT", "465")
    sender_email = os.environ.get("SENDER_EMAIL", "")
    sender_password = os.environ.get("SENDER_PASSWORD", "")
    recipient_email = os.environ.get("RECIPIENT_EMAIL", "")

    try:
        smtp_port = int(smtp_port_str)
    except ValueError:
        logger.error("Invalid SMTP_PORT value: %s. Must be a number.", smtp_port_str)
        return 1

    if not sender_email or not sender_password or not recipient_email:
        logger.error(
            "Missing required environment variables: "
            "SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL"
        )
        return 1

    # 获取石油市场数据
    logger.info("Fetching global oil market data...")
    oil_data = fetch_oil_prices()

    if not oil_data:
        logger.error("Failed to fetch any oil market data.")
        return 1

    # 格式化内容
    text_content = format_price_text(oil_data)
    html_content = format_price_html(oil_data)

    # 打印纯文本版本到控制台
    print(text_content)

    # 发送邮件
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"🛢️ 全球石油市场每日报告 - {today}"

    # 根据端口号决定使用 SSL 或 STARTTLS
    use_starttls = smtp_port == 587

    logger.info("Sending email report to %s...", recipient_email)
    success = send_email(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender_email=sender_email,
        sender_password=sender_password,
        recipient_email=recipient_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        use_starttls=use_starttls,
    )

    if success:
        logger.info("✅ Daily oil market report sent successfully!")
        return 0
    else:
        logger.error("❌ Failed to send the report email.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
