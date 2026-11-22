# Gmail API / OAuth 设置

软件不是要求 Gmail API key，而是要求每位用户建立自己的 **Google OAuth Desktop Client JSON**。所有 Gmail 登录都在 Google 官方网页完成。

官方参考：

- https://developers.google.com/workspace/gmail/api/quickstart/python
- https://developers.google.com/identity/protocols/oauth2/native-app

## 1. 建立 Google Cloud 项目

1. 打开 https://console.cloud.google.com/
2. 使用准备发送申请邮件的 Google/Gmail 账号登录。
3. 在顶部项目选择器建立一个新项目，例如 `Cisty`。

## 2. 启用 Gmail API

1. 打开 **APIs & Services → Library**。
2. 搜索 `Gmail API`。
3. 打开 Gmail API 后点击 **Enable**。

使用本软件不需要启用 Google Maps API，也不需要建立 Service Account。

## 3. 配置 Google Auth Platform

Google Cloud 的页面名称可能随账号类型略有不同：

1. 打开 **Google Auth Platform → Branding**。
2. 如果尚未配置，点击 **Get Started**。
3. App name 可填写 `Cisty`。
4. User support email 与 Contact information 填写自己的邮箱。
5. 如果页面提供 **Personal** 模式，而且只供自己使用，可选择 Personal。
6. 否则选择 **External**，将发布状态保持为 **Testing**，并在 **Audience / Test users** 加入自己的 Gmail 地址。

本软件直接调用 Gmail REST API，不是 Google Workspace MCP agent；建立 Client 时不要勾选 AI agent 选项。

## 4. 建立 Desktop OAuth Client

1. 打开 **Google Auth Platform → Clients**。
2. 点击 **Create Client**。
3. Application type 选择 **Desktop app**。
4. 名称可填写 `Cisty Windows`。
5. 点击 Create，然后下载 JSON 文件。
6. 把 JSON 保存在只有自己能访问的位置，例如 Documents，而不是公开网盘或 UserPack。

文件名可能是 `client_secret_...json`，不需要手动修改内容。

## 5. 在软件中选择 JSON

1. 打开 Cisty。
2. 进入 **My Workspace**。
3. 在 **Google OAuth credentials.json** 点击 Browse。
4. 选择刚才下载的 JSON。
5. 填写自己的 Gmail 地址并点击 **Save workspace**。

## 6. 第一次授权

第一次创建 Gmail Draft 或发送时：

1. 浏览器会打开 Google 登录页面。
2. 选择与 My Workspace 相同的 Gmail 账号。
3. 阅读权限说明后授权。
4. 如果自己的测试项目出现 `This app isn't verified`，确认浏览器显示的是自己刚建立的项目，再通过 Advanced 继续；不要对来源不明的项目这样操作。

软件使用 `gmail.modify` 权限创建草稿、发送、读取和回复本软件登记的 thread。程序逻辑不会扫描或显示其他未登记的邮箱对话。

## 安全规则

- 不要分享 OAuth JSON、Gmail token 或 Gmail 密码。
- 不要把 OAuth JSON 放进 UserPack、GitHub 或群聊。
- 想撤销权限时，可在 Google Account 的第三方连接/授权页面移除该应用。
- Testing 模式下 Google 可能要求定期重新授权；这是 Google 的安全策略，不是软件故障。
