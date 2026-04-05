"""
主程序入口
获取全球石油市场价格并发送邮件报告
"""

import sys
from datetime import datetime, timezone

from oil_market import fetch_all_oil_prices, format_html_report, format_plain_text_report
from send_email import send_email


def main() -> int:
    print("=" * 60)
    print("  全球石油市场每日报告 - 开始执行")
    print(f"  时间: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()

    # 1. 获取油价数据
    print("📡 正在获取全球石油市场数据...")
    prices = fetch_all_oil_prices()

    if not prices:
        print("❌ 未能获取到任何油价数据，程序退出")
        return 1

    # 2. 生成报告
    print("\n📝 正在生成报告...")
    plain_report = format_plain_text_report(prices)
    html_report = format_html_report(prices)

    # 打印纯文本报告到控制台
    print("\n" + plain_report)

    # 3. 发送邮件
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    subject = f"🛢️ 全球石油市场每日报告 - {today}"

    print("\n📧 正在发送邮件...")
    success = send_email(
        subject=subject,
        plain_body=plain_report,
        html_body=html_report,
    )

    if success:
        print("✅ 邮件发送成功！")
        return 0
    else:
        print("❌ 邮件发送失败，请检查 SMTP 配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())
