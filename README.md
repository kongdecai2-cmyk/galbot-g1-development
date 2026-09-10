# Galbot G1 二次开发协作仓库

这是用于银河通用机器人 Galbot G1 真机二次开发的团队私有仓库。当前项目使用 Galbot SDK 1.8.1，并记录了已核实的环境、真机测试结果、安全边界、训练示例和 SDK 资料索引。

本仓库不能让新的协作者或 GPT 自动继承历史对话、现场状态或工具环境。它提供的是结构化上下文；所有可能变化的机器人状态仍须在执行前重新核实。

## 新协作者和 GPT 的必读顺序

开始回答、修改代码或给出运行命令前，必须完整阅读：

1. `PROJECT_HANDOFF.md`：当前项目状态、已核实结果和安全边界。
2. `AGENTS.md`：项目工作规则和面向初学者的说明要求。
3. `GALBOT_PROJECT_MEMORY.md`：项目历史、环境、学习进度和未核实事项。
4. 涉及 SDK API、部署、建图/定位、传感器、运动规划或故障排查时，再读取 `GALBOT_SDK_1_8_1_REFERENCE.md` 的相关章节，并按页码查阅原始 PDF。

不得把知识库中的历史信息当成当前真机状态。版本、IP、权限、硬件、末端执行器、电量、地图、定位、机器人姿态和周边障碍物均可能变化。

## 安全警告

这是会控制真实机器人的代码。文件存在、语法检查通过或 SDK 返回 `SUCCESS`，都不等于真机动作安全或物理结果准确。

- 不要按文件编号依次运行 `training_examples/` 中的脚本。
- 任何运动测试都必须清空运动范围，并安排人员守在已测试可用的实体急停按钮旁。
- 无线断开、关闭 VS Code 和 `Ctrl+C` 不能替代实体急停。
- 不要未经审查直接运行全身回零、装箱、固定轨迹抓放或关闭碰撞检测的代码。
- 不要在仓库中提交密码、令牌、SSH 私钥、设备序列号或厂商默认凭据。

完整安全规则见 `PROJECT_HANDOFF.md` 和 `GALBOT_SDK_1_8_1_REFERENCE.md`。

## 仓库结构

```text
.
|-- AGENTS.md
|-- GALBOT_PROJECT_MEMORY.md
|-- GALBOT_SDK_1_8_1_REFERENCE.md
|-- Galbot_SDK_G1_1.8.1SDK、API开发文档.pdf
|-- PROJECT_HANDOFF.md
|-- README.md
|-- SHA256SUMS.txt
|-- docs/
|   `-- RESOURCES.md
|-- galbot_forward_left_forward_heart.py
|-- king_example_base_rotate_clockwise_360.py
`-- training_examples/
    |-- 01_example_sdk_check.py
    |-- 02_example_joint_control.py
    |-- 03_example_heart.py
    |-- 04_example_teach_pick_place_pose.py
    |-- 05_example_pick_place_fixed.py
    |-- 06_example_packing.py
    `-- 07_example_whole_body_reset_zero_odom.py
```

`training_examples/` 保存用户获授权共享的训练材料。文件名只说明训练顺序来源，不构成运行批准。各脚本实际风险与已知问题见 `PROJECT_HANDOFF.md`。

## 当前开发环境快照

- 开发电脑：Windows，使用 VS Code Remote SSH。
- 机器人 SSH：`galbot@192.168.102.49`。
- 机器人个人脚本目录：`/userdata/KDC`。
- 已核实兼容组合：SDK 1.8.1、GBS `GBS_1.16.0.2.rc88`，检查结果 `MATCH`。
- 机器人端 Python 历史截图显示为 3.8.10。

以上内容是 2026-09-10 的项目记录，不是永久配置。执行前按 `PROJECT_HANDOFF.md` 的“Information That Must Be Revalidated”重新检查。

## 团队开发流程

1. 从 `main` 创建短期功能分支，例如 `feature/read-odometry` 或 `fix/heart-timing-message`。
2. 每次只解决一个可验证的小目标，提交中说明代码改动、验证方法、真机是否实际运行以及剩余风险。
3. 修改 Python 文件后先做不运行程序的语法检查；在机器人上运行前，还须完成双端 SHA-256 校验。
4. 真机测试结果、重要风险、版本变化和确认过的新事实同步写入 `GALBOT_PROJECT_MEMORY.md`。
5. 合并前检查是否误提交了凭据、个人数据、运行日志或未授权的厂商材料。

Windows 到机器人的完整传输与验证流程见 `PROJECT_HANDOFF.md`。官方和补充资料见 `docs/RESOURCES.md`。

## 文件完整性

`SHA256SUMS.txt` 记录仓库交付文件的 SHA-256；它不包含自身，也不包含 `.git/`。`.gitattributes` 禁止 Git 自动改写受校验文本的换行符，以便不同系统克隆后仍能核对字节。校验值只能证明文件内容是否一致，不能证明脚本适合当前现场或可以安全运行。

## 授权边界

本仓库没有声明覆盖全部内容的统一开源许可证，仅供已获授权的团队在私有仓库内协作。SDK PDF、训练示例和其他厂商材料仍受其原始权利与适用协议约束，不因进入本仓库而改变授权条件。
