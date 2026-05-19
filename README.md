# 🛢️ 全球石油市场日报 (Daily Oil Market Report)

每天自动获取全球主要石油市场的最新价格，并将格式化报告发送至指定邮箱。

## 功能

- 每日北京时间 **08:00**（UTC 00:00）自动运行
- 支持手动触发（GitHub Actions → workflow_dispatch）
- 抓取以下品种的最新价格及日涨跌幅：

| 品种 | 交易所 |
|------|--------|
| WTI 原油 | NYMEX（纽约商品交易所） |
| 布伦特原油 | ICE（洲际交易所） |
| 天然气 | NYMEX |
| 汽油 RBOB | NYMEX |
| 取暖油 / 柴油 | NYMEX |

- 另附 OPEC 一篮子油价及迪拜/阿曼原油的官方数据链接
- 发送 **HTML 精美邮件** 和纯文本备用内容

## 快速开始

### 1. Fork / Clone 本仓库

### 2. 配置 GitHub Secrets

在仓库 **Settings → Secrets and variables → Actions** 中添加以下 Secret：

| Secret 名称 | 说明 | 必须 |
|------------|------|------|
| `EMAIL_SENDER` | 发件人邮箱地址 | ✅ |
| `EMAIL_PASSWORD` | 发件人邮箱密码或应用专用密码 | ✅ |
| `EMAIL_RECEIVER` | 收件人邮箱地址（可与发件人相同） | ✅ |
| `SMTP_HOST` | SMTP 服务器地址（默认：`smtp.gmail.com`） | 可选 |
| `SMTP_PORT` | SMTP 端口（默认：`587`） | 可选 |

> **Gmail 用户**：请在 Google 账号中开启「两步验证」，并生成「应用专用密码」填入 `EMAIL_PASSWORD`。

### 3. 启用 GitHub Actions

确认仓库的 Actions 功能已开启（Settings → Actions → General → Allow all actions）。  
工作流文件位于 `.github/workflows/daily_oil_report.yml`，将在每天 UTC 00:00 自动运行。

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量（或直接导出）
export EMAIL_SENDER="you@example.com"
export EMAIL_PASSWORD="your_app_password"
export EMAIL_RECEIVER="recipient@example.com"

# 运行
python src/oil_price_reporter.py
```

若未设置邮件环境变量，脚本会打印报告内容到终端并跳过发送。
若所有品种都抓取失败，脚本会返回非零退出码，方便 GitHub Actions 明确标红。

## 运行测试

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest tests/ -v
```

## GitHub Actions 行为

- 每日定时任务会先安装运行依赖和测试依赖
- 先跑测试，再执行抓取与发信
- 如果所有行情抓取都失败，workflow 会失败，避免悄悄发送一封全是错误的日报

## 数据来源

- **Yahoo Finance**（通过 [yfinance](https://github.com/ranaroussi/yfinance) 库获取期货价格）
- [OPEC 官网](https://www.opec.org/opec_web/en/data_graphs/40.htm)（OPEC 一篮子油价）
- [EIA 官网](https://www.eia.gov/dnav/pet/hist/rclc1d.htm)（迪拜/阿曼现货价）

> 价格仅供参考，不构成投资建议。
