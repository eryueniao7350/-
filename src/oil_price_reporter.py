"""
Daily global market brief with energy, precious metals, and FX quotes.
"""

import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


MARKET_SECTIONS = [
    {
        "key": "energy",
        "title": "能源",
        "title_en": "Energy",
        "symbols": {
            "CL=F": {
                "name": "WTI 原油 (纽约商品交易所)",
                "name_en": "WTI Crude Oil (NYMEX)",
                "unit": "USD/桶",
            },
            "BZ=F": {
                "name": "布伦特原油 (ICE)",
                "name_en": "Brent Crude Oil (ICE)",
                "unit": "USD/桶",
            },
            "NG=F": {
                "name": "天然气 (NYMEX)",
                "name_en": "Natural Gas (NYMEX)",
                "unit": "USD/MMBtu",
            },
            "RB=F": {
                "name": "汽油 (NYMEX RBOB)",
                "name_en": "Gasoline RBOB (NYMEX)",
                "unit": "USD/加仑",
            },
            "HO=F": {
                "name": "取暖油 / 柴油 (NYMEX)",
                "name_en": "Heating Oil (NYMEX)",
                "unit": "USD/加仑",
            },
        },
        "notes": [
            "OPEC 一篮子油价：https://www.opec.org/opec_web/en/data_graphs/40.htm",
            "迪拜/阿曼原油：https://www.eia.gov/dnav/pet/hist/rclc1d.htm",
        ],
    },
    {
        "key": "metals",
        "title": "贵金属",
        "title_en": "Precious Metals",
        "symbols": {
            "GC=F": {
                "name": "黄金 (COMEX)",
                "name_en": "Gold Futures (COMEX)",
                "unit": "USD/盎司",
            }
        },
        "notes": [],
    },
    {
        "key": "fx",
        "title": "外汇",
        "title_en": "Foreign Exchange",
        "symbols": {
            "USDCNY=X": {
                "name": "美元/人民币",
                "name_en": "USD/CNY",
                "unit": "CNY",
            },
            "USDJPY=X": {
                "name": "美元/日元",
                "name_en": "USD/JPY",
                "unit": "JPY",
            },
            "EURUSD=X": {
                "name": "欧元/美元",
                "name_en": "EUR/USD",
                "unit": "USD",
            },
        },
        "notes": [],
    },
]


def _error_item(symbol: str, meta: dict, error: str) -> dict:
    return {
        "symbol": symbol,
        "name": meta["name"],
        "name_en": meta["name_en"],
        "unit": meta["unit"],
        "price": None,
        "change": None,
        "change_pct": None,
        "error": error,
    }


def fetch_market_sections() -> list[dict]:
    """Fetch the latest quote for each configured market instrument."""
    try:
        import yfinance as yf
    except ImportError as exc:
        return [
            {
                "key": section["key"],
                "title": section["title"],
                "title_en": section["title_en"],
                "items": [
                    _error_item(symbol, meta, f"依赖缺失: {exc}")
                    for symbol, meta in section["symbols"].items()
                ],
                "notes": section["notes"],
            }
            for section in MARKET_SECTIONS
        ]

    results = []
    for section in MARKET_SECTIONS:
        items = []
        for symbol, meta in section["symbols"].items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if hist.empty:
                    items.append(_error_item(symbol, meta, "无数据"))
                    continue

                latest = hist.iloc[-1]
                price = round(float(latest["Close"]), 2)

                if len(hist) >= 2:
                    prev_close = round(float(hist.iloc[-2]["Close"]), 2)
                    change = round(price - prev_close, 2)
                    change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0
                else:
                    change = 0.0
                    change_pct = 0.0

                items.append(
                    {
                        "symbol": symbol,
                        "name": meta["name"],
                        "name_en": meta["name_en"],
                        "unit": meta["unit"],
                        "price": price,
                        "change": change,
                        "change_pct": change_pct,
                        "error": None,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                items.append(_error_item(symbol, meta, str(exc)))

        results.append(
            {
                "key": section["key"],
                "title": section["title"],
                "title_en": section["title_en"],
                "items": items,
                "notes": section["notes"],
            }
        )

    return results


def has_successful_quotes(sections: list[dict]) -> bool:
    """Return True when at least one instrument was fetched successfully."""
    return any(item["error"] is None for section in sections for item in section["items"])


def _change_html(change: float | None, change_pct: float | None) -> str:
    if change is None:
        return "<span style='color:#888'>N/A</span>"
    color = "#43a047" if change >= 0 else "#e53935"
    arrow = "▲" if change >= 0 else "▼"
    sign = "+" if change >= 0 else ""
    return (
        f"<span style='color:{color}'>"
        f"{arrow} {sign}{change:.2f} ({sign}{change_pct:.2f}%)"
        f"</span>"
    )


def build_html(sections: list[dict], report_time: str) -> str:
    section_blocks = ""
    note_blocks = []

    for section in sections:
        rows = ""
        for item in section["items"]:
            if item["error"]:
                price_cell = f"<td colspan='2' style='color:#e53935'>错误: {item['error']}</td>"
            else:
                price_cell = (
                    f"<td style='font-weight:bold'>{item['price']:.2f} <small>{item['unit']}</small></td>"
                    f"<td>{_change_html(item['change'], item['change_pct'])}</td>"
                )
            rows += f"""
            <tr>
              <td>{item['name']}</td>
              <td style='color:#666;font-size:12px'>{item['name_en']}</td>
              {price_cell}
            </tr>"""

        section_blocks += f"""
        <div class="section">
          <h2>{section['title']} <span>{section['title_en']}</span></h2>
          <table>
            <thead>
              <tr>
                <th>品种</th>
                <th>英文名称</th>
                <th>最新价格</th>
                <th>日涨跌</th>
              </tr>
            </thead>
            <tbody>
              {rows}
            </tbody>
          </table>
        </div>"""

        if section["notes"]:
            notes_html = "<br>".join(section["notes"])
            note_blocks.append(
                f"<div class='note'><strong>{section['title']}补充说明：</strong><br>{notes_html}</div>"
            )

    notes_section = "".join(note_blocks)

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background:#f5f5f5; margin:0; padding:0; }}
    .container {{ max-width:760px; margin:30px auto; background:#fff;
                  border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,.12); overflow:hidden; }}
    .header {{ background:#0f4c81; color:#fff; padding:24px 32px; }}
    .header h1 {{ margin:0; font-size:24px; }}
    .header p {{ margin:6px 0 0; font-size:13px; opacity:.85; }}
    .content {{ padding:24px 32px; }}
    .section {{ margin-bottom:24px; }}
    .section h2 {{ margin:0 0 12px; font-size:18px; color:#0f4c81; }}
    .section h2 span {{ color:#6b7280; font-size:14px; font-weight:normal; margin-left:6px; }}
    table {{ width:100%; border-collapse:collapse; }}
    th {{ background:#eaf2fb; color:#0f4c81; text-align:left; padding:10px 12px; font-size:13px; }}
    td {{ padding:10px 12px; border-bottom:1px solid #f0f0f0; font-size:14px; }}
    tr:last-child td {{ border-bottom:none; }}
    .note {{ font-size:13px; color:#555; background:#fff8e1;
             border-left:4px solid #ffc107; padding:10px 14px; margin-top:16px; border-radius:2px; }}
    .footer {{ background:#f5f5f5; padding:14px 32px; font-size:12px; color:#999; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🌍 全球市场晨报</h1>
      <p>报告时间：{report_time}（UTC）</p>
    </div>
    <div class="content">
      {section_blocks}
      {notes_section}
      <p style="font-size:12px;color:#999;margin-top:20px;">
        数据来源：Yahoo Finance。价格仅供参考，不构成投资建议。
      </p>
    </div>
    <div class="footer">
      本邮件由 GitHub Actions 自动生成并发送 · 每日北京时间 08:00 更新
    </div>
  </div>
</body>
</html>"""


def build_text(sections: list[dict], report_time: str) -> str:
    lines = [
        "=== 全球市场晨报 ===",
        f"报告时间：{report_time} (UTC)",
        "",
    ]

    for section in sections:
        lines.append(f"[{section['title']} / {section['title_en']}]")
        for item in section["items"]:
            if item["error"]:
                lines.append(f"{item['name']}: 错误 - {item['error']}")
            else:
                sign = "+" if item["change"] >= 0 else ""
                lines.append(
                    f"{item['name']}: {item['price']:.2f} {item['unit']}  "
                    f"({sign}{item['change']:.2f}, {sign}{item['change_pct']:.2f}%)"
                )
        if section["notes"]:
            lines.append("")
            lines.extend(section["notes"])
        lines.append("")

    lines.append("数据来源：Yahoo Finance。价格仅供参考，不构成投资建议。")
    return "\n".join(lines)


def send_email(html_body: str, text_body: str, report_time: str) -> None:
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["EMAIL_RECEIVER"]
    smtp_host = os.environ.get("SMTP_HOST") or "smtp.gmail.com"
    smtp_port = int(os.environ.get("SMTP_PORT") or "587")

    subject = f"🌍 全球市场晨报 - {report_time[:10]}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

    print(f"✅ 邮件已成功发送至 {receiver}")


def main() -> None:
    report_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"🔍 正在获取全球市场数据… ({report_time} UTC)")

    sections = fetch_market_sections()

    for section in sections:
        print(f"\n[{section['title']} / {section['title_en']}]")
        for item in section["items"]:
            if item["error"]:
                print(f"  ⚠️  {item['name']}: {item['error']}")
            else:
                sign = "+" if item["change"] >= 0 else ""
                print(
                    f"  ✔  {item['name']}: {item['price']:.2f} {item['unit']}  "
                    f"({sign}{item['change']:.2f}, {sign}{item['change_pct']:.2f}%)"
                )

    html = build_html(sections, report_time)
    text = build_text(sections, report_time)

    print("\n--- 纯文本报告 ---")
    print(text)

    if not has_successful_quotes(sections):
        print("\n❌ 所有品种都获取失败，停止发送邮件并返回非零退出码。")
        sys.exit(1)

    if all(k in os.environ for k in ("EMAIL_SENDER", "EMAIL_PASSWORD", "EMAIL_RECEIVER")):
        send_email(html, text, report_time)
    else:
        print(
            "\n⚠️  未设置邮件环境变量（EMAIL_SENDER / EMAIL_PASSWORD / EMAIL_RECEIVER），"
            "跳过发送。"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
