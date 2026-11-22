# Internship Workspace（Windows 桌面版）

当前主界面已经迁移到 PySide6。项目位于 [`InternshipAutoApply/`](InternshipAutoApply/)；完整架构、隐私边界与发布流程见 [`HANDOFF.md`](InternshipAutoApply/HANDOFF.md)。

## 已实现
- 导入 CareeReX `.xlsx`，按 `Target Faculty` 中真实的 `FOCS` token 筛选公司。
- 保留 Excel 的公司名称、官网、地址、城市、州属、行业、Target Faculty、是否接受国际学生实习等原始字段。
- SQLite 本地保存 HR Email、邮箱来源与人工核验状态、最近 Putrajaya Line 站、最后步行分钟、路线核实状态、申请状态和备注。
- 导入 Excel 时会按公司名称在所有工作表中匹配有 Email 栏的记录，并自动填入对应的邮箱候选值；候选值始终标记为「待核验」，不会直接用于投递。
- 公司列表可组合筛选行业、地区（含具体城市／州属）、已知步行距离、MRT／LRT／Monorail 线路与申请状态。
- 支持 MRT Putrajaya、MRT Kajang、LRT Kelana Jaya、LRT Ampang、LRT Sri Petaling 与 KL Monorail。系统可自动计算全部公司到最近站的直线距离，再按线路与距离筛选。
- Google Maps 公共交通路线链接。
- 英文申请邮件预览、Gmail Draft 创建、审核确认后发送、Resume PDF 附件。
- 每间公司都有「System email conversation」页：只显示本系统成功发送后建立的 Gmail 对话线程，选中公司后每分钟检查最新回复（也可立即手动刷新），并可从该线程发送跟进回复。
- 同一个 Gmail 可在学校、家里或新电脑之间同步 Cisty 已投记录。用户点击 `Sync Gmail` 后，软件只查询 `Cisty/Applications` 专用标签，恢复 Applied、Replied 和对应系统对话；不会扫描收件箱、其他已发送邮件或 Gmail 草稿。
- 不会猜测 HR Email；没有核实 HR Email、没有核实路线、没有 PDF Resume 时禁止发送。

## 运行要求
1. Windows 10/11。
2. 安装 Python 3.10 或更新版本，并勾选 Add Python to PATH。
3. 双击 `install.bat` 安装依赖。
4. 把原始 `CareeReX_IT_highlight.xlsx` 放在本文件夹，或启动后点 Import Excel。
5. 双击 `run_glass_ui.bat` 启动当前界面；`run.bat` 只作为旧 Tkinter 界面的回退入口。

## 第一次使用
1. 点 `Profile & Gmail Setup`，填写姓名、课程、实习期间、电话、Gmail。
2. 选择自己的 Resume PDF。
3. 配置 Gmail API OAuth：
   - 打开 https://console.cloud.google.com/
   - 建立/选择 Google Cloud project。
   - APIs & Services → Library → 启用 Gmail API。
   - OAuth consent screen 完成基本配置；若应用处于 Testing，将自己的 Gmail 加为 Test user。
   - APIs & Services → Credentials → Create Credentials → OAuth client ID → Desktop app。
   - 下载 JSON 文件，在软件设置中选择该 `credentials.json`。
   - 升级后首次创建 Draft／发送时会再次打开 Google 登录授权网页（用于升级旧版仅撰写权限的 token）。软件会请求 Gmail 读取／撰写权限，但只读取由本软件成功发送后登记的对话线程；不会扫描或显示其他收件箱邮件。不要把 Gmail 密码交给任何人。
4. 在公司列表中选公司，核对 Excel 自动填入的 Contact email（必须来自公司官网/可信招聘来源），勾选「I personally verified…」并保存。
5. 在 [Geoapify MyProjects](https://myprojects.geoapify.com/) 免费注册并创建 API key（无需信用卡；Free plan 为 3,000 requests/day）。在 `Profile & Gmail Setup` 贴上 `Geoapify free geocoding API key` 并保存。
6. 如只想处理某个行业／地区，先在列表选择 `Industry` 和／或 `Region`，按钮会改为 `Auto-calculate selected industry stations`。点击后只会计算该筛选范围内尚未计算的公司；选择 All industries 时才会计算全部公司。首次约需数分钟，坐标会缓存到本机，之后不会重复消耗请求。
7. 使用 `Transit line` 和距离筛选查看自动计算的附近公司。实际步行路线仍需点 `Open Google Maps route`，自行检查办公入口，填写最终步行分钟后按 Save 确认路线。
7. 选择公司并生成邮件预览。先用 `Create Gmail Draft` 检查 Gmail 草稿；正式发送用 `Review & Send`，在弹窗核对收件人、正文和附件后确认。
8. 换电脑时先导入相同的公司 Excel、在 My Workspace 登录同一个 Gmail，再点 `Sync Gmail`。旧版本用户应先在原电脑点一次 `Sync Gmail`，让软件只为原电脑已登记的 Cisty 对话补上同步标签。

## 重要说明
- Excel 只提供公司资料，不含可靠的 HR 邮箱、实时实习空缺、MRT 站点或办公楼入口步行时间。因此这些信息不会自动编造；需要逐家公司核实。
- 软件只会读取 Excel 中实际存在的邮箱栏并按公司名称配对；没有对应记录时不会猜测 HR 邮箱。它不会自动判断地图路线。
- 自动最近站计算使用 Geoapify 免费方案进行地址转换，并使用 OpenStreetMap 数据；不需要 Google Maps API Key 或 Billing。Geoapify Free plan 不会自动收费，超过每日额度时会拒绝请求。直线距离不等同实际步行路线；实际步行时间必须由用户在地图中核实。
- 「System email conversation」只保存本软件建立并带有 Cisty 专用标签的 Gmail thread。未通过本软件发送的邮箱往来及其他私人邮件不会被查询或显示。
- 发送前会再次弹窗要求确认。应用不会在后台无审核群发。
- 本地数据库 `internship_applications.db`、设置 `settings.json` 和 OAuth token（`token.json`／`token_messages.json`）请勿分享给他人；token 可在 Google Account 的第三方访问权限中撤销。
- 建议先用自己的备用邮箱做一次 Draft 测试。
code by Trez and Yee
