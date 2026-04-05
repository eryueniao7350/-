# 🛢️ 全球石油市场每日价格报告

自动获取全球主要石油市场的最新价格信息，并通过邮件发送每日报告。

Automatically fetches global oil market prices and sends a daily email report.

## 📊 监控的石油市场

| 市场 | 代码 | 说明 |
|------|------|------|
| WTI 原油 | CL=F | 美国西德克萨斯中质原油期货 (NYMEX) |
| 布伦特原油 | BZ=F | 国际基准原油期货 (ICE) |
| 上海原油 | SI=F | 上海国际能源交易中心原油期货 (INE) |

## 📧 报告内容

每日报告包含以下信息：
- 当前价格 (Current Price)
- 涨跌幅与百分比 (Price Change & Percentage)
- 昨日收盘价 (Previous Close)
- 日内最高/最低价 (Day High/Low)
- 成交量 (Volume)

报告同时提供纯文本和 HTML 格式，HTML 版本具有美观的卡片式布局。

## 🚀 快速开始

### 1. 配置 GitHub Secrets

在仓库的 **Settings → Secrets and variables → Actions** 中添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `SMTP_SERVER` | SMTP 服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口号 (SSL) | `465` |
| `SENDER_EMAIL` | 发件人邮箱地址 | `your-email@gmail.com` |
| `SENDER_PASSWORD` | 发件人密码或应用专用密码 | `xxxx xxxx xxxx xxxx` |
| `RECIPIENT_EMAIL` | 收件人邮箱地址 | `recipient@example.com` |

> **提示**：如果使用 Gmail，需要开启"应用专用密码"（App Password），而不是使用账户密码。
> 前往 [Google 账户安全设置](https://myaccount.google.com/apppasswords) 生成应用专用密码。

### 2. 自动运行

GitHub Actions 工作流已配置为 **每天 UTC 06:00（北京时间 14:00）** 自动运行。

你也可以在 **Actions** 标签页中手动触发工作流（workflow_dispatch）。

### 3. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="465"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@example.com"

# 运行
python main.py
```

## 📁 项目结构

```
.
├── .github/workflows/
│   └── oil-market-report.yml   # GitHub Actions 定时任务
├── src/
│   ├── __init__.py
│   ├── oil_market.py           # 石油市场数据获取与格式化
│   └── email_sender.py         # 邮件发送模块
├── main.py                     # 主程序入口
├── requirements.txt            # Python 依赖
└── README.md
```

## 🔧 常见 SMTP 配置

| 邮箱服务 | SMTP 服务器 | 端口 |
|---------|-------------|------|
| Gmail | smtp.gmail.com | 465 |
| Outlook/Hotmail | smtp-mail.outlook.com | 587 |
| QQ 邮箱 | smtp.qq.com | 465 |
| 163 邮箱 | smtp.163.com | 465 |

> **注意**：部分邮箱服务需要额外开启 SMTP 功能或生成授权码。

## 📝 数据来源

价格数据来自 [Yahoo Finance](https://finance.yahoo.com/)，通过 `yfinance` 库获取。

**免责声明**：本项目提供的数据仅供参考，不构成任何投资建议。