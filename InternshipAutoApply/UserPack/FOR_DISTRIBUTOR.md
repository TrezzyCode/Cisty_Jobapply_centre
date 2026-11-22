# 发布者打包清单

这是给软件发布者使用的文件；普通用户无需执行这里的构建步骤。

## 放入新版本

1. 在源码目录运行 `build_exe.bat`。
2. 等待生成 `dist\InternshipWorkspace.exe`。
3. 把该 EXE 复制到这个 `UserPack` 文件夹根目录，文件名必须保持为：

   `InternshipWorkspace.exe`

4. 双击 `verify_package.bat`。
5. 在一台没有开发环境的 Windows 电脑或新的 Windows 用户账户测试：
   - `install.bat`
   - 桌面快捷方式
   - Excel 导入
   - My Workspace 保存
   - Geoapify 站点计算
   - Gmail Draft
   - `uninstall.bat`
6. 确认 UserPack 内没有以下文件后再压缩：
   - `settings.json`
   - `*.db`
   - `token*.json`
   - `client_secret*.json` 或 `credentials.json`
   - 任何真实 Resume、头像或 API key
7. 将整个 `UserPack` 文件夹压缩为 ZIP 后分享。

## GitHub

EXE 和 ZIP 已被 `.gitignore` 排除，不会推送到源码仓库。若以后需要公开二进制版本，建议使用 GitHub Releases，而不是直接提交到 Git 历史。
