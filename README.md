# 🛢️ 全球石油市场每日报告

自动获取全球主要石油市场的价格信息，并通过邮件发送每日报告。

## 📊 覆盖的石油市场

| 市场 | 代码 | 说明 |
|------|------|------|
| WTI 原油 | CL=F | 美国西德克萨斯中质原油，美国基准价格 |
| 布伦特原油 | BZ=F | 国际基准原油价格 |
| 天然气 | NG=F | 亨利枢纽天然气期货 |
| 取暖油 | HO=F | 取暖油期货 |
| RBOB 汽油 | RB=F | 改良汽油混合料期货 |

## 📧 报告内容

每份报告包含以下信息：
- 当前价格
- 涨跌幅（与前一交易日相比）
- 开盘价、最高价、最低价、收盘价
- 成交量
- 交易所信息

邮件同时提供纯文本和 HTML 两种格式，HTML 格式包含美观的卡片式布局。

## ⚙️ 配置方法

### 1. 设置 GitHub Secrets

在仓库的 **Settings → Secrets and variables → Actions** 中添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `SMTP_SERVER` | SMTP 服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口号 | `587` |
| `SMTP_USERNAME` | SMTP 登录用户名（发件人邮箱） | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP 登录密码 | Gmail 请使用[应用专用密码](https://support.google.com/accounts/answer/185833) |
| `TO_EMAIL` | 收件人邮箱地址 | `recipient@example.com` |

### 2. 常用邮箱 SMTP 配置

**Gmail:**
- SMTP_SERVER: `smtp.gmail.com`
- SMTP_PORT: `587`
- 需要开启两步验证并创建应用专用密码

**Outlook/Hotmail:**
- SMTP_SERVER: `smtp-mail.outlook.com`
- SMTP_PORT: `587`

**QQ 邮箱:**
- SMTP_SERVER: `smtp.qq.com`
- SMTP_PORT: `587`
- 需要在 QQ 邮箱设置中开启 SMTP 服务并获取授权码

**163 邮箱:**
- SMTP_SERVER: `smtp.163.com`
- SMTP_PORT: `587`
- 需要在邮箱设置中开启 SMTP 服务并设置授权密码

### 3. 运行方式

- **自动运行**: 每天 UTC 00:00（北京时间 08:00）自动执行
- **手动运行**: 在 GitHub 仓库的 Actions 页面，选择 "全球石油市场每日报告" workflow，点击 "Run workflow"

## 🏗️ 项目结构

```
.
├── .github/workflows/
│   └── oil-market-report.yml   # GitHub Actions 工作流
├── src/
│   ├── main.py                 # 主程序入口
│   ├── oil_market.py           # 油价数据获取与报告生成
│   └── send_email.py           # 邮件发送模块
├── requirements.txt            # Python 依赖
└── README.md                   # 本文件
```

## 🔧 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export TO_EMAIL="recipient@example.com"

# 运行
cd src && python main.py
```

## 📝 注意事项

- 数据来源为 Yahoo Finance，仅供参考，不构成投资建议
- 邮件发送需要正确配置 SMTP 信息
- GitHub Actions 的 cron 调度可能会有几分钟的延迟
- 如果 Yahoo Finance API 不可用，相应市场会显示 "数据获取失败"