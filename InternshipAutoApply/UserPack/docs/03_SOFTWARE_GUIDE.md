# 软件使用教程

## 1. 设置 My Workspace

第一次打开软件会进入 My Workspace：

1. 填写姓名、课程、实习期间、电话和 Gmail。
2. 选择自己的 Resume PDF。
3. 选择自己的 Google OAuth Desktop Client JSON。
4. 填入自己的 Geoapify API key。
5. 可点击头像选择个人照片；不设置时会显示姓名首字母。
6. 点击 **Save workspace**。

资料只保存在当前 Windows 用户账户。

## 2. 导入公司 Excel

点击 **Import Excel** 选择 `.xlsx` 或 `.xlsm`。

当前导入格式需要包含：

- 第一栏：公司名称
- `Website`
- `Address 1`
- `City`
- `Industry`
- `Target Faculty`

程序会筛选 `Target Faculty` 中包含真实 `FOCS` token 的记录。若工作簿其他工作表同时包含公司名称与 Email 栏，软件会按公司名称匹配邮箱候选值。候选邮箱仍必须由用户核实。

## 3. 筛选公司

Applications 页可组合使用：

- Industry
- Region
- Distance
- Status
- Transit line
- 顶部搜索框

若只想计算某个行业或地区，请先选择筛选条件，再点击 Calculate stations。

## 4. 计算最近站点

- **Calculate stations**：计算当前筛选范围内尚无结果的公司。
- **Recalculate stations**：重新计算并覆盖当前筛选范围内的旧结果。

已保存的结果会在下次启动继续使用。可按 MRT Putrajaya、MRT Kajang、LRT Kelana Jaya、LRT Ampang、LRT Sri Petaling 与 KL Monorail 筛选。

## 5. 人工核实公司与路线

选择公司后，在右侧 Company 页检查：

1. 公司名称和完整地址。
2. Contact email 的来源与真实性。
3. 最近站点和所属线路。
4. 点击 **Open route** 查看实际地图路线。
5. 填写实际步行分钟。
6. 保存前确认自己确实检查过招聘邮箱和路线。

直线最近的站点不一定拥有最安全或最方便的步行入口，不能跳过人工检查。

## 6. 创建 Gmail Draft 或发送

1. 选择公司。
2. 确认招聘邮箱已核实。
3. 确认 Resume PDF 路径正确。
4. 生成 Email preview。
5. 建议先使用 **Create Gmail draft**，到 Gmail 再检查一次。
6. 使用 **Review & send** 时，必须在确认窗口检查收件人、正文和附件。

软件不会在后台自动群发。

## 7. 查看邮件来往

首次通过本软件发送后，该公司会建立一个 System conversation：

- 只显示该软件建立并登记的 Gmail thread。
- 可刷新最新回复。
- 可从软件内继续回复同一 thread。
- 软件外独立发送、未登记的邮件不会显示。

## 8. 更新软件

发布者提供新版 UserPack 后：

1. 关闭正在运行的软件。
2. 把完整新版 UserPack 解压到新的文件夹。
3. 再次运行 `install.bat`。

安装脚本会覆盖程序文件，但不会删除 `%LOCALAPPDATA%\IT Internship Auto Apply` 内的个人数据。
