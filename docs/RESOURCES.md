# Galbot G1 官方与补充资料

最后整理：2026-09-10

本页汇总项目中已经查阅或记录的资料入口。链接和在线内容会变化；使用前应核对页面版本、发布日期和当前机器人 SDK/GBS 组合。当前机器人使用 SDK 1.8.1，不能直接照搬 SDK 1.9.1 的接口、镜像或升级建议。

## SDK 与官方组织

| 资料 | 链接 | 项目中的用途与限制 |
| --- | --- | --- |
| 银河通用机器人官方 GitHub 组织 | https://github.com/GalaxyGeneralRobotics | 查找厂商公开仓库；具体仓库仍需核对许可证和版本。 |
| GalbotSDK 官方仓库 | https://github.com/GalaxyGeneralRobotics/GalbotSDK | SDK 公开代码、标签与许可证入口。 |
| GalbotSDK V1.8.1 标签 | https://github.com/GalaxyGeneralRobotics/GalbotSDK/releases/tag/V1.8.1 | 当前项目 SDK 版本对应的主要公开代码依据。 |
| SDK 1.8.1 在线文档 | https://developer.galbot.com/docs/SDK/1.8.1/g1/zh/ | 本项目原始 PDF 所指向的版本页面；在线内容可能更新或失效。 |
| SDK 1.9.1 在线文档 | https://developer.galbot.com/docs/SDK/1.9.1/g1/zh/ | 仅用于了解新版变化；不能作为当前 1.8.1 真机的直接执行依据。 |

## 产品、平台与培训

| 资料 | 链接 | 项目中的用途与限制 |
| --- | --- | --- |
| G1 使用手册 | https://developer.galbot.com/docs/g1/2.2.4/zh/g1 | 查询 G1 使用与安全信息；版本号与实际硬件版本须分别核实。 |
| 开发者平台 | https://developer.galbot.com/platform/ | 厂商开发服务入口；账号、权限和可用服务以团队授权为准。 |
| 官方训练营 | https://developer.galbot.com/training/ | 学习材料入口；示例不等于当前现场可直接安全运行。 |

## 模型与数据工具

| 资料 | 链接 | 项目中的用途与限制 |
| --- | --- | --- |
| G1 ROS 2、URDF、MJCF、USD 模型 | https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description | 仿真和机器人描述参考；使用前核对模型版本与实际硬件。 |
| MCAP 转 LeRobot 工具 | https://github.com/GalaxyGeneralRobotics/galbot-mcap2lerobot | 数据格式转换参考；当前项目尚未记录实际使用或验证结果。 |

## 仓库内资料的证据等级

- `GALBOT_SDK_1_8_1_REFERENCE.md` 是针对用户提供 PDF 的结构化索引与安全解读，不是厂商原文。
- `Galbot_SDK_G1_1.8.1SDK、API开发文档.pdf` 是带第三方水印的在线文档快照，不是厂商签名发布包。
- `GALBOT_PROJECT_MEMORY.md` 记录项目已核实事实、用户确认和待核实事项，但动态状态可能过期。
- 代码许可应以对应官方仓库和具体版本标签中的 `LICENSE` 为准；固件、模型、服务、数据和商业模块可能另受合同约束。
