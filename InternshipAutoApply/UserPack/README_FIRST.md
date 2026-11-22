# Internship Workspace 用户包

这个文件夹用于分发已经打包好的 Windows EXE。程序不会附带任何人的 Gmail 凭据、API key、简历、头像、数据库或申请记录；每位用户需要配置自己的资料。

## 第一次使用

1. 确认本文件夹内有 `InternshipWorkspace.exe`。
2. 双击 `verify_package.bat` 检查文件是否齐全。
3. 双击 `install.bat`。
4. 安装完成后，可从桌面或开始菜单打开 **Internship Workspace**。
5. 打开软件的 **My Workspace**，填写个人资料、选择 Resume PDF，并配置自己的 Gmail OAuth JSON 与 Geoapify API key。

安装不需要管理员权限。程序会安装到当前 Windows 用户的：

`%LOCALAPPDATA%\Programs\Internship Workspace`

用户数据会保存在：

`%LOCALAPPDATA%\IT Internship Auto Apply`

## 不想安装

可以双击 `run_portable.bat`，直接从这个文件夹运行 EXE。个人数据仍然会保存到上述 `%LOCALAPPDATA%` 用户数据目录。

## 配置顺序

建议依次阅读：

1. `docs\01_GMAIL_SETUP.md`
2. `docs\02_GEOAPIFY_SETUP.md`
3. `docs\03_SOFTWARE_GUIDE.md`
4. `docs\04_PRIVACY_AND_SAFETY.md`
5. `docs\05_TROUBLESHOOTING.md`

## 重要提醒

- 不要向软件作者或朋友索取、发送或共用 API key、OAuth JSON、Gmail token 或密码。
- Gmail 登录只会在 Google 官方网页进行；不要把 Gmail 密码输入软件。
- 软件只显示由本软件发出后登记的 Gmail 对话，不会显示其他私人邮件。
- 最近站点的自动距离是直线距离，实际步行路线和入口仍需人工核实。
