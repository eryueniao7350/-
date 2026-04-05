"""
全球主要石油市场信息获取模块
Fetches global oil market prices and information.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
import yfinance as yf
from jinja2 import Template

logger = logging.getLogger(__name__)

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M UTC"

# 全球主要石油期货代码 (Yahoo Finance tickers)
OIL_TICKERS = {
    "CL=F": "WTI 原油 (West Texas Intermediate)",
    "BZ=F": "布伦特原油 (Brent Crude)",
    "SC=F": "上海原油期货 (Shanghai INE Crude)",
}


@dataclass
class OilMarketData:
    """石油市场数据"""

    name: str
    ticker: str
    current_price: Optional[float]
    previous_close: Optional[float]
    change: Optional[float]
    change_percent: Optional[float]
    day_high: Optional[float]
    day_low: Optional[float]
    volume: Optional[int]
    currency: str
    timestamp: str


def fetch_oil_prices() -> list[OilMarketData]:
    """获取全球主要石油市场的价格数据"""
    results = []

    for ticker_symbol, name in OIL_TICKERS.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.fast_info
            hist = ticker.history(period="2d")

            if hist.empty:
                logger.warning("No data available for %s (%s)", name, ticker_symbol)
                results.append(
                    OilMarketData(
                        name=name,
                        ticker=ticker_symbol,
                        current_price=None,
                        previous_close=None,
                        change=None,
                        change_percent=None,
                        day_high=None,
                        day_low=None,
                        volume=None,
                        currency="USD",
                        timestamp=datetime.now(timezone.utc).strftime(
                            TIMESTAMP_FORMAT
                        ),
                    )
                )
                continue

            current_price = float(hist["Close"].iloc[-1])
            previous_close = (
                float(hist["Close"].iloc[-2]) if len(hist) > 1 else None
            )
            day_high = float(hist["High"].iloc[-1])
            day_low = float(hist["Low"].iloc[-1])
            raw_volume = hist["Volume"].iloc[-1]
            volume = int(raw_volume) if pd.notna(raw_volume) and raw_volume > 0 else None

            change = None
            change_percent = None
            if previous_close is not None and previous_close != 0:
                change = round(current_price - previous_close, 2)
                change_percent = round((change / previous_close) * 100, 2)

            currency = getattr(info, "currency", "USD") or "USD"

            results.append(
                OilMarketData(
                    name=name,
                    ticker=ticker_symbol,
                    current_price=round(current_price, 2),
                    previous_close=(
                        round(previous_close, 2) if previous_close else None
                    ),
                    change=change,
                    change_percent=change_percent,
                    day_high=round(day_high, 2),
                    day_low=round(day_low, 2),
                    volume=volume,
                    currency=currency,
                    timestamp=datetime.now(timezone.utc).strftime(
                        TIMESTAMP_FORMAT
                    ),
                )
            )
            logger.info("Successfully fetched data for %s: $%.2f", name, current_price)

        except Exception:
            logger.exception("Error fetching data for %s (%s)", name, ticker_symbol)
            results.append(
                OilMarketData(
                    name=name,
                    ticker=ticker_symbol,
                    current_price=None,
                    previous_close=None,
                    change=None,
                    change_percent=None,
                    day_high=None,
                    day_low=None,
                    volume=None,
                    currency="USD",
                    timestamp=datetime.now(timezone.utc).strftime(
                        TIMESTAMP_FORMAT
                    ),
                )
            )

    return results


def format_price_text(data_list: list[OilMarketData]) -> str:
    """将石油价格数据格式化为纯文本"""
    now = datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
    lines = [
        "=" * 60,
        f"  全球主要石油市场每日价格报告",
        f"  Global Oil Market Daily Report",
        f"  报告时间: {now}",
        "=" * 60,
        "",
    ]

    for data in data_list:
        lines.append(f"📊 {data.name}")
        lines.append(f"   代码 (Ticker): {data.ticker}")

        if data.current_price is not None:
            lines.append(f"   当前价格 (Price): ${data.current_price:.2f} {data.currency}")

            if data.change is not None:
                arrow = "📈" if data.change >= 0 else "📉"
                sign = "+" if data.change >= 0 else ""
                lines.append(
                    f"   涨跌幅 (Change): {arrow} {sign}{data.change:.2f} "
                    f"({sign}{data.change_percent:.2f}%)"
                )

            if data.previous_close is not None:
                lines.append(f"   昨日收盘 (Prev Close): ${data.previous_close:.2f}")

            if data.day_high is not None and data.day_low is not None:
                lines.append(
                    f"   今日区间 (Day Range): ${data.day_low:.2f} - ${data.day_high:.2f}"
                )

            if data.volume is not None:
                lines.append(f"   成交量 (Volume): {data.volume:,}")
        else:
            lines.append("   ⚠️ 数据暂不可用 (Data unavailable)")

        lines.append(f"   更新时间: {data.timestamp}")
        lines.append("-" * 60)
        lines.append("")

    lines.append("=" * 60)
    lines.append("  数据来源: Yahoo Finance")
    lines.append("  免责声明: 本报告仅供参考，不构成投资建议。")
    lines.append("  Disclaimer: For reference only, not investment advice.")
    lines.append("=" * 60)

    return "\n".join(lines)


def format_price_html(data_list: list[OilMarketData]) -> str:
    """将石油价格数据格式化为 HTML 邮件内容"""
    template_str = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
  .container { max-width: 680px; margin: 0 auto; background: #fff; border-radius: 12px;
               box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }
  .header { background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff;
            padding: 28px 32px; text-align: center; }
  .header h1 { margin: 0 0 6px 0; font-size: 22px; }
  .header p { margin: 0; font-size: 13px; opacity: 0.8; }
  .content { padding: 24px 32px; }
  .oil-card { border: 1px solid #e8e8e8; border-radius: 8px; padding: 18px 20px;
              margin-bottom: 16px; transition: box-shadow 0.2s; }
  .oil-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
  .oil-name { font-size: 16px; font-weight: 600; color: #1a1a2e; margin-bottom: 10px; }
  .price-row { display: flex; align-items: baseline; margin-bottom: 8px; }
  .price { font-size: 28px; font-weight: 700; color: #333; }
  .change-up { color: #16a34a; font-size: 15px; margin-left: 12px; font-weight: 600; }
  .change-down { color: #dc2626; font-size: 15px; margin-left: 12px; font-weight: 600; }
  .details { font-size: 13px; color: #666; line-height: 1.8; }
  .details span { margin-right: 18px; }
  .unavailable { color: #999; font-style: italic; padding: 8px 0; }
  .footer { background: #fafafa; padding: 16px 32px; text-align: center;
            font-size: 12px; color: #999; border-top: 1px solid #eee; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🛢️ 全球石油市场每日报告</h1>
    <p>Global Oil Market Daily Report &mdash; {{ report_time }}</p>
  </div>
  <div class="content">
    {% for item in data_list %}
    <div class="oil-card">
      <div class="oil-name">{{ item.name }}</div>
      {% if item.current_price is not none %}
      <div class="price-row">
        <span class="price">${{ "%.2f"|format(item.current_price) }}</span>
        {% if item.change is not none %}
          {% if item.change >= 0 %}
        <span class="change-up">📈 +{{ "%.2f"|format(item.change) }} (+{{ "%.2f"|format(item.change_percent) }}%)</span>
          {% else %}
        <span class="change-down">📉 {{ "%.2f"|format(item.change) }} ({{ "%.2f"|format(item.change_percent) }}%)</span>
          {% endif %}
        {% endif %}
      </div>
      <div class="details">
        {% if item.previous_close is not none %}
        <span>昨收: ${{ "%.2f"|format(item.previous_close) }}</span>
        {% endif %}
        {% if item.day_high is not none and item.day_low is not none %}
        <span>区间: ${{ "%.2f"|format(item.day_low) }} - ${{ "%.2f"|format(item.day_high) }}</span>
        {% endif %}
        {% if item.volume is not none %}
        <span>成交量: {{ "{:,}"|format(item.volume) }}</span>
        {% endif %}
      </div>
      {% else %}
      <div class="unavailable">⚠️ 数据暂不可用 (Data currently unavailable)</div>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  <div class="footer">
    <p>数据来源: Yahoo Finance | 免责声明: 本报告仅供参考，不构成投资建议。</p>
    <p>Data source: Yahoo Finance | Disclaimer: For reference only, not investment advice.</p>
  </div>
</div>
</body>
</html>"""

    template = Template(template_str)
    now = datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
    return template.render(data_list=data_list, report_time=now)
