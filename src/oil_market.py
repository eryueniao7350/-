"""
全球主要石油市场价格获取模块
Fetches global oil market prices from public APIs.
"""

import json
import logging
from datetime import datetime, timezone

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 主要石油市场及其对应的 Yahoo Finance 符号
OIL_MARKETS = {
    "WTI 原油 (West Texas Intermediate)": "CL=F",
    "布伦特原油 (Brent Crude)": "BZ=F",
    "天然气 (Natural Gas)": "NG=F",
    "取暖油 (Heating Oil)": "HO=F",
    "RBOB 汽油 (RBOB Gasoline)": "RB=F",
}

YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_price_from_yahoo(symbol: str) -> dict | None:
    """从 Yahoo Finance 获取单个品种的价格数据"""
    try:
        params = {"range": "2d", "interval": "1d"}
        resp = requests.get(
            YAHOO_FINANCE_URL.format(symbol=symbol),
            headers=HEADERS,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        result = data["chart"]["result"][0]
        meta = result["meta"]
        quote = result["indicators"]["quote"][0]
        timestamps = result["timestamp"]

        # 获取最新一天的数据
        idx = -1
        price_info = {
            "current_price": meta.get("regularMarketPrice"),
            "previous_close": meta.get("chartPreviousClose"),
            "currency": meta.get("currency", "USD"),
            "exchange": meta.get("exchangeName", "N/A"),
            "open": quote["open"][idx] if quote["open"][idx] else None,
            "high": quote["high"][idx] if quote["high"][idx] else None,
            "low": quote["low"][idx] if quote["low"][idx] else None,
            "close": quote["close"][idx] if quote["close"][idx] else None,
            "volume": quote["volume"][idx] if quote["volume"][idx] else None,
            "date": datetime.fromtimestamp(timestamps[idx], tz=timezone.utc).strftime(
                "%Y-%m-%d"
            ),
        }

        # 计算涨跌幅
        if price_info["current_price"] and price_info["previous_close"]:
            change = price_info["current_price"] - price_info["previous_close"]
            change_pct = (change / price_info["previous_close"]) * 100
            price_info["change"] = round(change, 2)
            price_info["change_pct"] = round(change_pct, 2)
        else:
            price_info["change"] = None
            price_info["change_pct"] = None

        return price_info

    except Exception:
        logger.exception("Failed to fetch price for %s", symbol)
        return None


def fetch_all_oil_prices() -> dict:
    """获取所有石油市场的价格数据"""
    results = {}
    for market_name, symbol in OIL_MARKETS.items():
        logger.info("Fetching price for %s (%s)...", market_name, symbol)
        price_data = fetch_price_from_yahoo(symbol)
        if price_data:
            results[market_name] = price_data
            logger.info(
                "  %s: $%.2f (%s%.2f%%)",
                market_name,
                price_data["current_price"],
                "+" if (price_data.get("change_pct") or 0) >= 0 else "",
                price_data.get("change_pct") or 0,
            )
        else:
            results[market_name] = {"error": "数据获取失败"}
            logger.warning("  %s: Failed to fetch data", market_name)
    return results


def format_plain_text_report(prices: dict) -> str:
    """生成纯文本格式的报告"""
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "=" * 60,
        f"  全球主要石油市场每日报告",
        f"  报告时间: {now}",
        "=" * 60,
        "",
    ]

    for market_name, data in prices.items():
        lines.append(f"📊 {market_name}")
        lines.append("-" * 40)

        if "error" in data:
            lines.append(f"  ⚠️  {data['error']}")
        else:
            lines.append(f"  当前价格:  ${data['current_price']:.2f} {data['currency']}")
            if data.get("change") is not None:
                arrow = "🔺" if data["change"] >= 0 else "🔻"
                sign = "+" if data["change"] >= 0 else ""
                lines.append(
                    f"  涨跌幅:    {arrow} {sign}{data['change']:.2f} ({sign}{data['change_pct']:.2f}%)"
                )
            if data.get("open"):
                lines.append(f"  开盘价:    ${data['open']:.2f}")
            if data.get("high"):
                lines.append(f"  最高价:    ${data['high']:.2f}")
            if data.get("low"):
                lines.append(f"  最低价:    ${data['low']:.2f}")
            if data.get("close"):
                lines.append(f"  收盘价:    ${data['close']:.2f}")
            if data.get("volume"):
                lines.append(f"  成交量:    {data['volume']:,.0f}")
            lines.append(f"  交易所:    {data.get('exchange', 'N/A')}")
            lines.append(f"  数据日期:  {data.get('date', 'N/A')}")

        lines.append("")

    lines.append("=" * 60)
    lines.append("此报告由 GitHub Actions 自动生成并发送")
    lines.append("数据来源: Yahoo Finance")
    lines.append("=" * 60)

    return "\n".join(lines)


def format_html_report(prices: dict) -> str:
    """生成 HTML 格式的邮件报告"""
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head><meta charset='utf-8'></head>",
        "<body style='font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px;'>",
        "<div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;'>",
        "<h1 style='margin: 0;'>🛢️ 全球石油市场每日报告</h1>",
        f"<p style='margin: 10px 0 0 0; opacity: 0.8;'>报告时间: {now}</p>",
        "</div>",
        "<br>",
    ]

    for market_name, data in prices.items():
        if "error" in data:
            html_parts.append(
                f"<div style='border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px;'>"
                f"<h3 style='margin: 0 0 10px 0;'>📊 {market_name}</h3>"
                f"<p style='color: #999;'>⚠️ {data['error']}</p></div>"
            )
            continue

        change_color = "#27ae60" if (data.get("change") or 0) >= 0 else "#e74c3c"
        arrow = "▲" if (data.get("change") or 0) >= 0 else "▼"
        sign = "+" if (data.get("change") or 0) >= 0 else ""

        change_text = ""
        if data.get("change") is not None:
            change_text = f"{sign}{data['change']:.2f} ({sign}{data['change_pct']:.2f}%)"

        html_parts.append(
            f"<div style='border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px;'>"
            f"<h3 style='margin: 0 0 10px 0; color: #2c3e50;'>📊 {market_name}</h3>"
            f"<div style='display: flex; align-items: baseline; gap: 15px; flex-wrap: wrap;'>"
            f"<span style='font-size: 28px; font-weight: bold; color: #2c3e50;'>${data['current_price']:.2f}</span>"
            f"<span style='font-size: 16px; color: {change_color}; font-weight: bold;'>{arrow} {change_text}</span>"
            f"</div>"
            f"<table style='width: 100%; margin-top: 10px; font-size: 14px; color: #555;'>"
            f"<tr><td>开盘: ${data['open']:.2f if data.get('open') else 'N/A'}</td>"
            f"<td>最高: ${data['high']:.2f if data.get('high') else 'N/A'}</td>"
            f"<td>最低: ${data['low']:.2f if data.get('low') else 'N/A'}</td></tr>"
        )
        if data.get("volume"):
            html_parts.append(
                f"<tr><td colspan='3'>成交量: {data['volume']:,.0f}</td></tr>"
            )
        html_parts.append(
            f"<tr><td colspan='3'>交易所: {data.get('exchange', 'N/A')} | 数据日期: {data.get('date', 'N/A')}</td></tr>"
            f"</table></div>"
        )

    html_parts.extend(
        [
            "<div style='text-align: center; color: #999; font-size: 12px; margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee;'>",
            "<p>此报告由 GitHub Actions 自动生成并发送</p>",
            "<p>数据来源: Yahoo Finance | 仅供参考，不构成投资建议</p>",
            "</div>",
            "</body></html>",
        ]
    )

    return "\n".join(html_parts)


if __name__ == "__main__":
    prices = fetch_all_oil_prices()
    print(format_plain_text_report(prices))
    print("\n\nJSON Data:")
    print(json.dumps(prices, indent=2, ensure_ascii=False))
