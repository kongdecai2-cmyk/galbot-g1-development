# Galbot G1 SDK 1.8.1 参考知识库

最后整理：2026-09-10

## 用途与证据等级

这是对用户提供的《Galbot SDK G1 1.8.1 SDK、API 开发文档》进行的**结构化学习笔记和接口索引**，不是 PDF 的逐页复制件。它用于后续回答 SDK、部署、建图、定位、Python API 和排障问题时快速定位原始依据。

原始文件：`E:\WXWork\1688856602736104\Cache\File\2026-09\Galbot_SDK_G1_1.8.1SDK、API开发文档.pdf`

- 已核实来源：PDF 共 589 页，封面标注 G1 系列、SDK 1.8.1、生成于 2026-08-24，来源网址为 `developer.galbot.com/docs/SDK/1.8.1/g1/zh/`。
- 文档性质：该 PDF 位于微信缓存且带水印，是在线文档快照，不是厂商签名的离线发布包。接口内容可作为 1.8.1 的重要参考；网络、部署、许可、设备配置等动态内容必须在真机和对应官方标签中复核。
- 当前项目已核实组合：机器人 SDK `1.8.1`，GBS `GBS_1.16.0.2.rc88`，兼容性检查结果为 `MATCH`。这不授权升级到 SDK 1.9.1。
- 页码约定：下文“PDF p.N”指该 PDF 的物理页码。

阅读与使用优先级：先读本文件的“安全边界”和“最小工作流”；需要某个接口时再查看对应索引和 PDF 页码；真正执行运动前，以当前机器人实际版本、已安装 SDK 的本地帮助和现场状态为准。

## 1. 系统与架构

### 1.1 SDK 的能力分层

PDF p.30-32 将能力分为三层：

- 基础能力：关节/轨迹/末端/底盘控制，RGB/深度图、雷达、IMU、力传感器等数据读取，音频和指示灯，状态、日志和资源释放。
- 高级能力：FK/IK、单链与全身规划、碰撞检测、动态障碍物、工具和目标物管理，以及导航、SLAM 和避障。
- 业务能力：分拣、料箱搬运等需额外商业授权的模块。它们不属于当前基础 SDK 开发默认可用范围。

### 1.2 HPU 与 XCU

PDF p.35、p.568、p.580 的定义如下：

| 单元 | 文档定义的主要职责 | 初学者应该怎样理解 |
| --- | --- | --- |
| HPU / Orin | 视觉、AI 推理、规划、导航、SLAM 等高算力任务 | 处理“看、想、规划”的服务端 |
| XCU | 电机、关节执行、实时控制、模式管理 | 处理“真正让关节和底盘动起来”的实时端 |

排障时，能连接但控制不动优先按 XCU 控制链路排查；能动但地图、规划、感知异常优先按 HPU 服务排查（PDF p.568）。这是文档给出的经验分类，不是绝对诊断结论。

### 1.3 运行环境

PDF p.34 说明：PC 推荐 Ubuntu 22.04（支持 Ubuntu 20.04-24.04）、x86_64；机器人为 aarch64；Python 支持 3.8-3.14；推荐 16 GB 存储。当前项目是在机器人端 Python 3.8.10 上运行，符合该范围。

## 2. 使用前必须理解的概念、单位和坐标系

### 2.1 单位

除非 API 自己另有说明，按下表理解，不能把角度制直接填入接口：

| 数据 | 单位 | PDF 依据 |
| --- | --- | --- |
| 关节位置 | 弧度 rad | p.38、p.375-376 |
| 关节速度 | rad/s | p.150、p.375 |
| 线位置、夹爪开口、障碍物安全距离 | 米 m | p.36、p.38、p.371 |
| 底盘线速度 | m/s | p.38、p.432 |
| 底盘角速度、yaw、欧拉角 | rad 或 rad/s | p.38-39、p.432-433 |
| 时间/超时 | 秒 s；传感器时间戳为 ns | p.38、p.371 |
| 夹爪力 | 文档示例使用 N；实际末端能力需实物复核 | p.116 |

角度换算：`弧度 = 角度 * pi / 180`。例如 90 度约等于 1.571 rad。不要依据肉眼猜测关节正负方向，先读取当前位置并进行小幅、低速、单组测试。

### 2.2 关键坐标系

PDF p.37-39：

- `base_link`：随机器人底盘一起移动的基座坐标系。
- `odom`：基于轮式里程计的相对坐标系，累计误差会随运动增加。
- `map`：建图/定位建立的全局坐标系，导航通常依赖它。
- 位姿统一为 `[x, y, z, qx, qy, qz, qw]`，位置单位为米、四元数顺序为 `xyzw`。
- 平面底盘位姿是 `[x, y, yaw]`，其中 x/y 为米、yaw 为弧度。

**不能混用 `odom` 与 `map`。** `odom` 适合短时相对运动；`map` 只有完成建图和良好定位后才可靠。把一个 `map` 中的目标直接当作 `odom` 指令，可能造成与预期完全不同的运动。

### 2.3 关节组与实际配置

PDF p.148、p.369-371 给出的 G1 组名：

| 组名 | 文档中的典型自由度/用途 |
| --- | --- |
| `head` | 2 个关节，头部/相机朝向 |
| `leg` | 5 个关节，躯干和下部姿态 |
| `left_arm` / `right_arm` | 各 7 个关节，抓取和操作 |
| `left_gripper` / `right_gripper` | 夹爪开合 |
| `left_suction_cup` / `right_suction_cup` | 吸盘操作 |
| `left_dexhand` / `right_dexhand` | 可选灵巧手 |
| `chassis` | 底盘状态组；底盘运动应走底盘 API，不应用关节位置接口模拟 |

这是 SDK 的模型和典型配置，不证明当前真机装有每一种末端。调用前必须用 `get_joint_group_names()`、`get_joint_names(True, groups)` 或实际只读状态确认可用组。若 API 同时收到 `joint_groups` 和非空 `joint_names`，后者优先（PDF p.148、p.369）。

### 2.4 传感器名称和帧

PDF p.148 列出典型 `SensorType` 与帧：头部左右相机、左右臂 RGB/深度相机、`BASE_LIDAR`（`lidar_base_link`）、`TORSO_IMU`（`imu_base_link`）、四路环视相机和底盘超声波。传感器真实可用性取决于当前硬件和初始化时传入的集合。

获取外参优先用 `get_sensor_extrinsic(sensor_id)`；需要任意帧变换时用 `get_transform(target_frame, source_frame)`；先用 `get_frame_names()` 读取真机实际 TF 名称，避免硬编码猜错（PDF p.148、p.444-445）。

## 3. 安全边界：文档内容不等于默认安全操作

### 3.1 每次真机运动前的最低条件

1. 现场人员确认实体急停可触及、可用，且指定一名观察者。
2. 清空底盘行进区域和双臂扫掠空间，确认地面、负载、姿态和电量适合测试。
3. 先做只读验证，再做单关节或单组件、小幅、低速、有超时的动作。
4. 运动命令必须检查返回状态；发送失败、超时、通信断开都不能继续下一步。
5. `finally` 中尝试停止和释放 SDK 资源，但它不是实体急停的替代品；Wi-Fi 断开、关闭 VS Code、按 Ctrl+C 都不能当可靠急停。

PDF p.578-579 说明急停触发会停止运动和执行机构，但设备未必断电；解锁后才可再次接收命令。现场安全培训和厂商手册优先于本笔记。

### 3.2 明确禁止作为新手默认方案的 PDF 内容

下列命令或做法确实存在于 PDF 中，但在本项目默认**不执行**：

- 递归 `chmod 777`、关闭全部防火墙、手工改 HPU/XCU 底层网络文件（PDF p.50-76、p.78、p.582）。它们会扩大安全暴露或破坏设备网络配置。
- 关闭自碰撞/环境碰撞检查（PDF p.113、p.116、p.363-364）。关闭会使规划或执行轨迹失去保护。
- 高频 `set_joint_commands`、`set_joint_commands_batch`、`PublishTarget`、`RequestTarget`、旁路 PVT 控制器（PDF p.150、p.232-242）。这是高级实时控制接口，不是首次运动的入口。
- `reload_controller`、`acquire_controller`、`release_controller`、`start_controller`、`stop_controller`、底层服务重启和解除关节限位（PDF p.437-439、p.570-574）。它们可能改变控制权、服务状态或机械安全状态，应由厂商支持或有经验人员处理。
- 教程 5 的抓取流程（PDF p.109-116）：它包含占位的虚拟目标识别、固定目标姿态、关闭碰撞检查和导航，不能在真实场景直接运行。

### 3.3 状态码

PDF p.364-365 定义常见 `ControlStatus`：`SUCCESS`、`TIMEOUT`、`FAULT`、`INVALID_INPUT`、`INIT_FAILED`、`IN_PROGRESS`、`STOPPED_UNREACHED`、`DATA_FETCH_FAILED`、`PUBLISH_FAIL`、`COMM_DISCONNECTED`。除 `SUCCESS` 外，初学阶段一律视为“停止当前流程并记录输出”，不要盲目重试运动。

## 4. Python 程序最小结构

PDF p.149 的生命周期模式：初始化，等待数据准备，执行少量业务逻辑，发出关闭请求，等待，销毁资源。

```python
from galbot_sdk.g1 import GalbotRobot
import time

robot = GalbotRobot()
if not robot.init():
    raise RuntimeError("SDK init failed")

try:
    time.sleep(1)  # 等待首批状态/传感器数据
    # 先只读，再在安全条件满足时下发一个小动作
finally:
    robot.request_shutdown()
    robot.wait_for_shutdown()
    robot.destroy()
```

理由：`init()` 成功只是 SDK 通信和订阅准备成功；文档明确提示启动后数据可能尚未就绪（PDF p.149）。`finally` 让异常路径也尽力清理资源。`destroy()` 是 SDK 资源释放，不会把机器人自动移动到安全姿态。

传感器读取应在 `init(enable_sensor_set)` 中显式启用需要的传感器后再读取；未启用或未准备好时可得到空值（PDF p.175、p.178、p.440-445）。不要在示例中用 `os.system("pip install ...")` 自动安装依赖，先确认机器人环境和版本再安装。

## 5. GalbotRobot：最常用的基础接口

以下签名以 PDF 示例和 API 参考为依据。Python 绑定的细小类型或默认参数可能随安装包变化；在改写新程序前，应在已连接机器人上以 `help()` 或对应 1.8.1 示例再次核对。

### 5.1 只读接口，建议学习顺序

| 目的 | 接口/典型调用 | 返回或注意 | PDF 依据 |
| --- | --- | --- | --- |
| 列出关节名 | `get_joint_names(only_active_joint, joint_groups)` | 不要手写关节名；先看真机返回顺序 | p.171、p.369-370 |
| 读取位置 | `get_joint_positions(joint_groups, joint_names)` | 关节位置为 rad；非空 `joint_names` 优先 | p.170-171 |
| 读取完整关节状态 | `get_joint_states(joint_groups, joint_names)` | 位置、速度、加速度、力矩、电流 | p.169-170 |
| 夹爪状态 | `get_gripper_state(G1JointGroup.left_gripper)` | 含 width(m)、velocity(m/s)、effort、is_moving | p.171-172、p.371 |
| 吸盘状态 | `get_suction_cup_state(group)` | 压力、激活状态、动作状态 | p.172-173 |
| IMU | `get_imu_data(SensorType.TORSO_IMU)` | 传感器需在 init 时启用；加速度 m/s^2、角速度 rad/s | p.174-175、p.440 |
| 里程计 | `get_odom()` | 读取位置、姿态、线/角速度；可用于记录，不自动保证地图定位 | p.440-441 |
| 电池 | `get_bms_information()` | 读取电压、电流、电量、温度等；运动前仍需现场判断 | p.176-177 |
| 设备信息 | `get_device_information()` | 型号、固件、硬件版本等；序列号不写入项目记忆 | p.175-176、p.441 |
| 坐标变换 | `get_transform(target_frame, source_frame, timestamp_ns=0, timeout_ms=100)` | 返回 `[x,y,z,qx,qy,qz,qw]` 和 ns 时间戳；失败可能为空 | p.173-174、p.444 |
| 相机/雷达 | `get_rgb_data`、`get_depth_data`、`get_lidar_data` | 必须预先启用传感器；深度以 `depth_scale` 转换，不能猜单位 | p.177-179、p.441-443 |
| 标定参数 | `get_camera_intrinsic`、`get_sensor_extrinsic` | 需预先启用；外参可用 `base_link` 作参考 | p.179-180、p.443-445 |

### 5.2 低频关节位置控制

```python
status = robot.set_joint_positions(
    joint_pos,       # 与选择的关节严格一一对应，单位 rad
    joint_groups,    # 例如 ["head"]
    joint_names,     # 若非空则覆盖 joint_groups
    is_blocking,     # True: 等达到目标或超时再返回
    max_speed,       # rad/s
    timeout_s,       # s
)
```

PDF p.150-151：该接口会做速度受限插值，适合一次性、低频的点位移动；**不适合**高频模型推理输出，连续调用会导致不连续和延迟。初学者的第一项动作优先选这个接口，且只针对已确认的单一关节组，以较低 `max_speed` 和阻塞/超时方式执行。

前置核对：关节组存在、目标数组长度和实际关节数相符、姿态与目标之间不会碰撞、急停和观察者已就位。若 `status != ControlStatus.SUCCESS`，停止后续动作，读取状态和日志，不要把同一命令自动重复多次。

### 5.3 末端执行器

- `set_gripper_command(group, width, speed, effort, is_blocking)`：PDF p.151 及 p.116 示例表明夹爪宽度单位为 m、速度 m/s，力的适用范围必须按当前实际夹爪确认。
- `set_suction_cup_command(...)`：用于吸盘，不能把夹爪参数套用到吸盘。
- 当前真机左右端具体装配尚未核实。任何末端控制代码必须先做只读状态检查，确认组名与实物一致。

### 5.4 底盘：速度、姿态与停止

`set_base_velocity(linear_velocity, angular_velocity, duration_s)`（PDF p.169、p.432）：

- `linear_velocity = [vx, vy, vz]`，单位 m/s；`angular_velocity = [wx, wy, wz]`，单位 rad/s。
- 底盘通常使用 `vx` 与 `wz`；`duration_s` 到期后 SDK 示例说明会自动停止。
- 这是速度开环控制，不会因“运行了理论时间”就证明真实位移或转角准确。

`set_base_pose(x, y, yaw, frame_id="odom", reference_frame_id="odom", ...)`（PDF p.432-434）：以目标位置/航向控制底盘。只有完全理解坐标系、底盘控制器、定位质量和周边环境后才使用。

`stop_base()`（PDF p.435）：请求立即停止移动底盘。每个含底盘速度的脚本都应在异常路径和 `finally` 中尝试调用；它是软件保护，不能代替实体急停。

### 5.5 高风险全身/控制器接口

- `zero_whole_body_and_base(...)`：会让全身关节和底盘归零（PDF p.435-437）。不是“重置代码状态”，而是实际大范围运动；目前不作为练习入口。
- `stop_trajectory_execution()`：停止当前关节轨迹并保持当前位置（PDF p.437）。
- `switch_controller`、`acquire_controller`、`release_controller`、`start_controller`、`stop_controller`、`reload_controller`：涉及硬件控制权和控制器生命周期（PDF p.437-440）。无厂商指导不得用它们“解决不动”。
- `publish_target` / `request_target`：需要直接构造底层 `SingoriXTarget`，底盘还要手工切换 pose/twist 控制器（PDF p.232-242）。只面向高级实时控制开发。

## 6. GalbotMotion、Navigation、Perception

### 6.1 GalbotMotion：运动学和规划

用途：FK/IK、末端位姿、关节/笛卡尔轨迹、碰撞检查、障碍物与工具管理（PDF p.30-31）。教程 5 使用了 `get_end_effector_pose`、`get_end_effector_pose_on_chain` 和 `set_end_effector_pose`（PDF p.111-116）。

原则：末端位姿控制不是“填入一个 xyz 就能安全运动”。它至少依赖：正确末端 frame、参考 frame、当前关节状态、可达性、碰撞模型、工具和障碍物信息。文档允许 `enable_collision_check=False`，但 PDF p.363-364 明确警告这会导致危险轨迹；本项目默认要求 `True`，并且在无完成安全建模/现场核对前不执行末端自动运动。

IK 容差的平移单位为 m、旋转单位为 rad；增加求解超时可能得到更多种子尝试，但也延迟响应（PDF p.371-375）。初学阶段不要靠放宽容差或关闭碰撞检查来“让 IK 成功”。

### 6.2 GalbotNavigation：建图、定位和导航

导航不是底盘速度控制的替代品。它的正确依赖链为：

`雷达服务 -> 建图并保存 -> 地图清理/电子围栏 -> 定位 -> 定位质量检查 -> 路径可达性检查 -> 导航`

PDF p.77-87 的已核实条件：

- 新机在启用定位/导航服务前应先完成建图，否则可能进入异常模式。
- 建图时要确认雷达服务存在；保存地图后，应有 `global_cloud_cleaned.pcd` 供定位使用。
- 电子围栏不是装饰项，目的是阻止进入楼梯、危险区或非工作区。
- 定位使用目标地图目录 `cur`；开始导航前应有正常位姿发布且定位评分大于 `0.75`。
- 环境明显变化时旧地图会降低定位和路径质量。PDF 的地图更新示例要求较高定位评分并改系统配置，属于厂商/熟练用户维护项。

教程 5 使用的导航调用形态是：先读当前位姿，再 `check_path_reachability(goal_pose, cur_pose)`，之后 `navigate_to_goal(goal_pose, enable_collision_check=True, is_blocking=True, timeout=20)`，最后检查 `check_goal_arrival()`（PDF p.112）。这仅说明接口工作流，不证明任何固定 goal 对当前场地安全。

### 6.3 GalbotPerception：感知服务

PDF p.361-362：先 `init(enabled_modules)` 加载指定模块和模型，等待约 10 秒准备，再 `run_once(module)`；用 `wait_for_new_result(module, timeout_s)` 等待结果，`get_latest_result(module)` 获取缓存结果。模型、传感器和模块授权是否实际可用必须在当前机器人核实。

PDF 教程中的 `detect_target()` 是占位函数，直接返回固定 pose（p.114）。它不是视觉识别算法，不能据此得出机器人已经具备自动抓取能力。

## 7. 文档教程的正确学习定位

| 教程主题 | 文档页码 | 能学到什么 | 当前项目建议 |
| --- | --- | --- | --- |
| Example 1 基础控制/比心 | p.88-90 | init、读角度、阻塞点位、清理 | 高风险双臂动作，仅阅读，不直接运行 |
| 相机/点云示例 | p.101-109 | 传感器启用、RGB/深度解码、点云 | 可改成只读和不落地文件的检查练习 |
| Example 5 抓取放置 | p.109-116 | 导航、视觉、TF、末端、夹爪的整合结构 | 仅作架构阅读；禁止按原样真机运行 |
| Python 基础示例 | p.147-186 | 各基础 API 的最小调用方式 | 优先读取状态、关节名、传感器；运动需另行审核 |
| Motion/Navigation/Perception 示例 | PDF 后续章节 | 规划、导航、推理的接口模式 | 在完成安全、地图、校准与硬件核实后分步学习 |

## 8. 部署、网络与文件传输

PDF p.42-48 的机器人端部署模式适合在机器人 HPU 上运行，特点是低网络延迟；PDF p.49 起提供 PC 端远程部署。当前项目已通过同一 Wi-Fi 用 VS Code Remote SSH 连接机器人并在机器人端运行 Python，属于机器人端开发工作流。

原 PDF 的部署命令和路径在不同版本可能不同，例如 Docker 小节出现 1.8.0 镜像名称。因此：

1. 每次更改 SDK 前先执行 `galbot_sdk check-version`，只在版本兼容且有厂商发布说明时升级。
2. 不记录或复述文档中出现的默认账户口令；账号、认证方式和 IP 必须由授权管理员在现场提供。
3. 本项目 Windows 到机器人传输固定采用：本机 SHA-256 -> `scp -p` 上传 -> 机器人 `sha256sum` 比对 -> `python3 -m py_compile` 语法检查。详情见 `GALBOT_PROJECT_MEMORY.md`。
4. 当前个人脚本目录为 `/userdata/KDC`，但目录权限和文件内容应在每次运行前核实。

## 9. 故障排查的安全路由

PDF p.567-588 的推荐顺序有价值，但其中某些修复需要 root 权限或会改变底层服务。项目采用以下分级：

### 可以由初学者先做的只读检查

1. 观察实体急停是否已释放，确认现场无危险。
2. 收集完整的程序输出、SDK/GBS 兼容性结果和发生时间。
3. 在授权的正确设备上读取工作模式、相关日志和服务状态；先判断问题位于 HPU 还是 XCU。
4. 检查 SDK 程序是否正确初始化、传感器是否在 `init` 时启用、返回状态是否为 `SUCCESS`。
5. 底盘问题还要确认电量；PDF p.573 写明 SOC 低于 25% 时底盘会停机保护。

### 必须暂停并找厂商支持/有经验人员的操作

- ABNORMAL 模式下重启 launcher 或其他底层服务。
- 解除限位、抱闸或电机操作、修改 URDF 限位。
- 修改 HPU/XCU 系统网络配置、系统服务配置、末端 `robot_config.toml`、相机配置。
- 对底层日志、core 文件作 root 级排障，或执行会改变持久配置的修复。

原因：这些操作可能让控制器状态、硬件配置或安全约束与实际机器人不一致。PDF p.570-582 提供的是售后排障资料，不能因“文档里有命令”就当成普通开发步骤。

## 10. 许可和版本差异

PDF p.589 的许可页描述软件为保密专有软件；公开 GitHub 的 GalbotSDK V1.8.1 标签含 Apache-2.0 LICENSE。两者存在文本冲突。处理原则：

- 对开源仓库代码，以实际使用的官方标签中的 `LICENSE` 为准。
- 对 GBS 固件、模型、服务、数据和商业业务模块，假定可能另受合同或授权约束，未经明确授权不复制、分发或改动。
- 当前机器人使用 SDK 1.8.1。在线 1.9.1 文档只能用来了解变化，不能直接复制接口、Docker 镜像、部署命令或版本建议到当前机器人。

## 11. 后续回答的执行规则

当用户询问“怎么开发某功能”时，按下面顺序回答和执行：

1. 先指出是否缺少硬件、末端、地图、碰撞模型、传感器、权限或安全前提。
2. 明确哪些是 PDF 已核实事实，哪些需要在当前机器人重新核实。
3. 先设计一个不动机器人或只读的小验证程序。
4. 只有用户确认输出和现场安全条件后，才提出下一步低风险动作。
5. 每个 Python 示例解释：导入、初始化、参数单位、返回值、异常/停止逻辑、资源清理、预期结果及风险。
6. 任何脚本传输均遵守 SHA-256 校验工作流；任何真机结果和重要新事实写回 `GALBOT_PROJECT_MEMORY.md`。

## 原始文档快速索引

| 主题 | PDF 页码 |
| --- | --- |
| 产品概述、系统要求、术语、版本检查 | p.30-40 |
| 机器人端/PC 端部署 | p.42-76 |
| 建图、电子围栏、定位 | p.77-87 |
| 入门教程 | p.88-146 |
| Python 示例和基础 API 使用 | p.147-217 |
| 高级目标 Publish/Request 示例 | p.232-242 |
| 传感器、枚举、控制状态、碰撞配置 | p.363-445（及相邻 API 页） |
| 故障排除 | p.567-588 |
| PDF 许可页 | p.589 |
