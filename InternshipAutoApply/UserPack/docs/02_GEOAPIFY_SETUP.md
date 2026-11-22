# Geoapify 免费 API 设置

Geoapify 用于把公司地址转换为坐标。软件随后使用免费的站点坐标与直线距离计算最近 MRT/LRT/Monorail 站点，不需要 Google Maps Routes API。

官方参考：

- https://www.geoapify.com/get-started-with-maps-api/
- https://apidocs.geoapify.com/docs/geocoding/

## 申请 API key

1. 打开 https://myprojects.geoapify.com/
2. 注册或登录自己的 Geoapify 账号。
3. 建立一个项目，例如 `Internship Workspace`。
4. 打开项目的 **API Keys**。
5. 复制自动生成的 API key。
6. 打开软件的 **My Workspace**。
7. 把 key 贴到 **Geoapify free API key**。
8. 点击 **Save workspace**。

Geoapify 官方说明当前 Free plan 不需要信用卡，每个账号的免费项目共享每日 3,000 credits。超过额度时请求会返回 HTTP 429，不会自动转成付费订阅。

## 正确使用方式

1. 先选择 Industry 与 Region。
2. 点击 **Calculate stations**，只计算当前筛选范围内尚未计算的公司。
3. 计算结果会保存在本地数据库，重新打开软件不需要重复计算。
4. 只有需要覆盖旧结果时才点击 **Recalculate stations**。

## 注意

- API key 每人自行申请，不要共用作者的 key。
- 如果 key 泄露，请在 Geoapify 项目中重新生成并替换。
- 公司地址不完整时，Geoapify 可能找不到位置；先补全地址再计算。
- 自动结果是直线距离，不等于实际步行距离。
- 最终步行分钟必须打开地图路线并由用户核实。
