# 隐私与安全

## 本地保存的数据

每个 Windows 用户的数据保存在：

`%LOCALAPPDATA%\IT Internship Auto Apply`

可能包含：

- 应用设置与个人资料
- 公司与申请状态数据库
- 已计算的站点结果
- Gmail OAuth token
- 本软件登记的 Gmail 对话内容
- 个人头像副本

Resume 与 OAuth JSON 通常保存在用户自己选择的位置，软件只保存路径。

## 不应分享的内容

- `%LOCALAPPDATA%\IT Internship Auto Apply` 整个文件夹
- `settings.json`
- `internship_applications.db`
- `token_messages.json`
- OAuth/credentials/client_secret JSON
- Geoapify API key
- Resume、电话、私人邮箱、头像

## Gmail 边界

软件需要 Gmail `gmail.modify` 权限以建立草稿、发送、读取回复和继续同一 thread。跨电脑同步只列出 `Cisty/Applications` 标签下的 thread，并只为本地已登记的旧 Cisty thread 补标签；由于 Gmail 不允许给 draft 添加自定义标签，程序会读取 Draft 列表的邮件头，但只接受带 `X-Cisty-App: Cisty` 私有标记的草稿。它不会扫描收件箱或其他已发送邮件，也不会显示私人草稿。

Gmail 同步内容限于：Cisty 草稿、已投状态、回复状态、发送时间、thread ID 与该 Cisty 对话内容。个人资料、API key、OAuth JSON、token、简历、头像、公司 Excel 和交通站点计算不会上传到 Gmail。

## 邮件发送安全

- Excel 中发现的邮箱只是候选值，不代表真实招聘地址。
- 用户必须自行从公司官网或可信招聘来源核实。
- 正式发送前必须检查收件人、正文与附件。
- 不要向大量未确认地址群发，以免造成垃圾邮件或账号限制。

## 备份

更新或重置电脑前，可关闭软件后备份 `%LOCALAPPDATA%\IT Internship Auto Apply`。备份本身包含私人数据，应加密保存，不要上传公共网盘或 GitHub。

## 卸载

`uninstall.bat` 只移除程序与快捷方式，不删除用户数据。若确定不再需要数据，请先备份，再由用户本人手动处理上述本地数据文件夹。
