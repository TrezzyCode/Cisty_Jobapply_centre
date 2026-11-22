# 常见问题

## Windows SmartScreen 阻止运行

自行打包、没有数字签名的 EXE 可能触发 SmartScreen。只有在确认 UserPack 来自可信发布者且文件未被篡改时，才选择 **More info → Run anyway**。

## install.bat 显示找不到 EXE

确认 `Cisty.exe` 与 `install.bat` 位于同一个 UserPack 根目录，且文件名没有被浏览器改成 `(1)` 或其他名称。

## Gmail 显示 Access denied / Error 403

- 确认 Gmail API 已启用。
- 确认 OAuth Client 类型为 Desktop app。
- External + Testing 模式下，确认自己的 Gmail 已加入 Test users。
- 确认软件中的 Gmail 与浏览器授权账号一致。

## Gmail token expired / revoked

1. 关闭软件。
2. 打开 `%LOCALAPPDATA%\IT Internship Auto Apply`。
3. 先备份，再将 `token_messages.json` 改名，例如 `token_messages.old.json`。
4. 重新打开软件并执行 Gmail 操作，浏览器会要求再次授权。

不要删除数据库或 settings 来解决 Gmail 授权问题。

## A 电脑显示 Applied，B 电脑显示 Not applied

1. 在 A 电脑升级到含 Gmail Sync 的版本，并点一次 **Sync Gmail**。
2. 在 B 电脑导入相同公司 Excel，确认 My Workspace 的 Gmail 地址相同。
3. 在 B 电脑点 **Sync Gmail**。
4. 若显示 `Waiting for company-list import`，代表 Gmail 记录安全存在，但 B 电脑的公司列表尚无可匹配公司；导入完整 Excel 后再同步。
5. 若提示 Gmail 账号不一致，请删除本机 `%LOCALAPPDATA%\IT Internship Auto Apply\token_messages.json`，重新操作并在 Google 官方页面选择正确账号。删除 token 只会要求重新授权，不会删除 Gmail 邮件或本地公司资料。

## Cisty 显示未响应，并出现黑色 cmd 窗口

旧启动脚本会让 Cisty 与 cmd 共用控制台。若控制台标题显示“选择 / Select”，Windows QuickEdit 会暂停 Python，Cisty 因此显示未响应。新版 `run_glass_ui.bat` 已改用 `pythonw.exe`，不会保留黑色控制台窗口。

- 临时恢复旧版本：在黑色窗口按 `Esc` 或 `Enter` 退出选择状态。
- 永久解决：使用新版启动脚本或之后打包的 `Cisty.exe`。
- 不要连续双击多次；新版会拦截第二个实例。
- 若新版仍发生真正错误，查看 `%LOCALAPPDATA%\IT Internship Auto Apply\cisty_error.log`，其中不应包含简历或 Gmail 密码。

## Geoapify 401 / 403

API key 不正确、已停用或复制时带有空格。到 Geoapify MyProjects 重新复制 key，并在 My Workspace 保存。

## Geoapify 429

当天免费额度已用完。等待额度重置后再继续；不要不断点击 Recalculate stations。

## Company address could not be located

地址可能过短、缺少 postcode/city/state，或包含 Excel 中的异常字符。补全公司地址后再重新计算。无法确认的公司应保留为未计算，而不是猜测坐标。

## 选择 Transit line 后没有公司

先清除 Distance 筛选，确认目标公司的站点已经计算。尚未计算的公司不会自动属于某条线路。然后针对当前 Industry / Region 运行 Calculate stations。

## 邮件无法发送

检查：

- 招聘邮箱是否存在并已人工核实
- Resume 是否为可访问的 PDF
- Gmail OAuth JSON 是否仍在原路径
- Gmail 授权是否成功
- 网络连接是否正常

## 界面显示不完整

- 将窗口最大化。
- Windows 显示缩放建议先测试 100%、125% 或 150%。
- 使用最新版软件；不要混用旧的 `run.bat` Tkinter 界面。

## 想重置软件但保留恢复机会

1. 关闭软件。
2. 将 `%LOCALAPPDATA%\IT Internship Auto Apply` 重命名为带日期的备份文件夹。
3. 重新启动软件，它会建立新的空白数据目录。

确认新环境正常且旧数据确实不需要后，再决定是否删除备份。
