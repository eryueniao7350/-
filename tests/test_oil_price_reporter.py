"""
Tests for oil_price_reporter.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from oil_price_reporter import build_html, build_text, _change_html


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_PRICES = [
    {
        "symbol": "CL=F",
        "name": "WTI 原油 (纽约商品交易所)",
        "name_en": "WTI Crude Oil (NYMEX)",
        "unit": "USD/桶",
        "price": 82.50,
        "change": 1.20,
        "change_pct": 1.48,
        "error": None,
    },
    {
        "symbol": "BZ=F",
        "name": "布伦特原油 (ICE)",
        "name_en": "Brent Crude Oil (ICE)",
        "unit": "USD/桶",
        "price": 86.10,
        "change": -0.50,
        "change_pct": -0.58,
        "error": None,
    },
    {
        "symbol": "NG=F",
        "name": "天然气 (NYMEX)",
        "name_en": "Natural Gas (NYMEX)",
        "unit": "USD/MMBtu",
        "price": None,
        "change": None,
        "change_pct": None,
        "error": "无数据",
    },
]

REPORT_TIME = "2024-01-15 00:00:00"


# ---------------------------------------------------------------------------
# Tests for _change_html
# ---------------------------------------------------------------------------

def test_change_html_positive():
    html = _change_html(1.20, 1.48)
    assert "▲" in html
    assert "+1.20" in html
    assert "+1.48%" in html
    assert "#43a047" in html  # green for positive (price rise)


def test_change_html_negative():
    html = _change_html(-0.50, -0.58)
    assert "▼" in html
    assert "-0.50" in html
    assert "-0.58%" in html
    assert "#e53935" in html  # red for negative


def test_change_html_none():
    html = _change_html(None, None)
    assert "N/A" in html


# ---------------------------------------------------------------------------
# Tests for build_text
# ---------------------------------------------------------------------------

def test_build_text_contains_header():
    text = build_text(SAMPLE_PRICES, REPORT_TIME)
    assert "全球石油市场日报" in text
    assert REPORT_TIME in text


def test_build_text_contains_wti():
    text = build_text(SAMPLE_PRICES, REPORT_TIME)
    assert "WTI 原油" in text
    assert "82.50" in text
    assert "+1.20" in text


def test_build_text_contains_brent_negative():
    text = build_text(SAMPLE_PRICES, REPORT_TIME)
    assert "布伦特原油" in text
    assert "86.10" in text
    assert "-0.50" in text


def test_build_text_error_item():
    text = build_text(SAMPLE_PRICES, REPORT_TIME)
    assert "天然气" in text
    assert "错误" in text


def test_build_text_contains_links():
    text = build_text(SAMPLE_PRICES, REPORT_TIME)
    assert "https://www.opec.org/opec_web/en/data_graphs/40.htm" in text
    assert "https://www.eia.gov/dnav/pet/hist/rclc1d.htm" in text


# ---------------------------------------------------------------------------
# Tests for build_html
# ---------------------------------------------------------------------------

def test_build_html_is_html():
    html = build_html(SAMPLE_PRICES, REPORT_TIME)
    assert html.strip().startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_build_html_contains_price():
    html = build_html(SAMPLE_PRICES, REPORT_TIME)
    assert "82.50" in html
    assert "86.10" in html


def test_build_html_contains_error():
    html = build_html(SAMPLE_PRICES, REPORT_TIME)
    assert "无数据" in html


def test_build_html_contains_report_time():
    html = build_html(SAMPLE_PRICES, REPORT_TIME)
    assert REPORT_TIME in html


def test_build_html_contains_opec_link():
    html = build_html(SAMPLE_PRICES, REPORT_TIME)
    assert "https://www.opec.org/opec_web/en/data_graphs/40.htm" in html
