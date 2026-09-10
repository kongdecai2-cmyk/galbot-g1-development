"""Run a nominal base-motion sequence, then launch the supplied heart script.

Sequence: move forward about 1 metre, turn left about 90 degrees, move
forward about 1 metre, then run /userdata/basic_day1/03_example_heart.py.

This uses timed velocity control. Distance and angle are estimates, not
closed-loop measurements, and can vary with floor conditions and wheel slip.
"""

import math
import os
import subprocess
import sys
import time

from galbot_sdk.g1 import ControlStatus, GalbotRobot


# Keep the motion slow for the first real-robot trial.
LINEAR_SPEED_M_S = 0.10
ANGULAR_SPEED_RAD_S = 0.10
FORWARD_DISTANCE_M = 1.0
LEFT_TURN_ANGLE_DEG = 90.0
HEART_SCRIPT_PATH = "/userdata/basic_day1/03_example_heart.py"

ZERO_VELOCITY = [0.0, 0.0, 0.0]
FORWARD_LINEAR_VELOCITY = [LINEAR_SPEED_M_S, 0.0, 0.0]
# Positive wz is the usual base_link right-hand convention for a left turn.
# The actual direction has not been verified on this robot for this script.
LEFT_TURN_ANGULAR_VELOCITY = [0.0, 0.0, ANGULAR_SPEED_RAD_S]


def wait_interruptibly(duration_s: float) -> None:
    """Wait in short intervals so KeyboardInterrupt is handled promptly."""
    deadline = time.monotonic() + duration_s
    while True:
        remaining_s = deadline - time.monotonic()
        if remaining_s <= 0.0:
            return
        time.sleep(min(0.1, remaining_s))


def stop_base_with_retries(robot: GalbotRobot, attempts: int = 3) -> bool:
    """Ask the SDK to stop the base and report whether it acknowledged it."""
    for attempt in range(1, attempts + 1):
        status = robot.stop_base()
        if status == ControlStatus.SUCCESS:
            print("底盘停止成功。")
            return True
        print(f"底盘停止失败，第 {attempt}/{attempts} 次，状态: {status}")
        time.sleep(0.2)

    print("无法通过 SDK 确认底盘停止，请立即按实体急停按钮。")
    return False


def run_base_stage(
    robot: GalbotRobot,
    stage_name: str,
    linear_velocity: list,
    angular_velocity: list,
    duration_s: float,
) -> None:
    """Run one timed base stage, then explicitly request a stop."""
    print(f"{stage_name}：预计 {duration_s:.2f} 秒。")
    status = robot.set_base_velocity(
        linear_velocity,
        angular_velocity,
        duration_s,
    )
    if status != ControlStatus.SUCCESS:
        raise RuntimeError(f"{stage_name}指令下发失败，状态: {status}")

    wait_interruptibly(duration_s + 0.2)
    if not stop_base_with_retries(robot):
        raise RuntimeError(f"{stage_name}后未能确认底盘停止")


def run_heart_script() -> None:
    """Launch the original heart script only after the base sequence stopped."""
    if not os.path.isfile(HEART_SCRIPT_PATH):
        raise FileNotFoundError(f"未找到比心脚本: {HEART_SCRIPT_PATH}")

    print(f"正在调用比心脚本: {HEART_SCRIPT_PATH}")
    result = subprocess.run([sys.executable, HEART_SCRIPT_PATH], check=False)
    if result.returncode != 0:
        raise RuntimeError(f"比心脚本退出码为 {result.returncode}")


def shutdown_robot(robot: GalbotRobot) -> None:
    """Release this SDK client before another script initializes its own client."""
    robot.request_shutdown()
    robot.wait_for_shutdown()
    robot.destroy()
    print("SDK 资源已释放。")


def main() -> int:
    """Initialize the SDK, perform the sequence, then release resources."""
    robot = GalbotRobot()
    initialized = False

    forward_duration_s = FORWARD_DISTANCE_M / LINEAR_SPEED_M_S
    turn_duration_s = math.radians(LEFT_TURN_ANGLE_DEG) / ANGULAR_SPEED_RAD_S

    try:
        print("正在初始化 GalbotRobot...")
        if not robot.init():
            print("GalbotRobot 初始化失败，程序不会下发运动指令。")
            return 1
        initialized = True
        time.sleep(1.0)

        print("\n本次动作是开环定时控制：前进 1 米和左转 90 度均为名义值。")
        print("运行前必须确认：")
        print("1. 前方和左转后的行进区域均已清空，且预留足够的机器人与双臂扫掠空间。")
        print("2. 机器人未连接充电线，机械臂姿态紧凑、安全，比心动作范围内没有障碍物。")
        print("3. 有一名人员全程守在已测试可用的实体急停按钮旁。")
        print("4. 你已确认正向 vx 为前进；本脚本假设正 wz 从上方看为左转。")
        confirmation = input(
            "全部确认后输入 RUN_SEQUENCE；输入其他内容将退出："
        ).strip()
        if confirmation != "RUN_SEQUENCE":
            print("未收到完整安全确认，取消执行。")
            return 0

        print("机器人将在 3 秒后开始前进。")
        for seconds in (3, 2, 1):
            print(seconds)
            time.sleep(1.0)

        run_base_stage(
            robot,
            "第 1 段：前进约 1 米",
            FORWARD_LINEAR_VELOCITY,
            ZERO_VELOCITY,
            forward_duration_s,
        )
        run_base_stage(
            robot,
            "第 2 段：左转约 90 度",
            ZERO_VELOCITY,
            LEFT_TURN_ANGULAR_VELOCITY,
            turn_duration_s,
        )
        run_base_stage(
            robot,
            "第 3 段：前进约 1 米",
            FORWARD_LINEAR_VELOCITY,
            ZERO_VELOCITY,
            forward_duration_s,
        )

        print("底盘三段动作完成且已停止。")
        heart_confirmation = input(
            "确认当前位置周围适合双臂比心后，输入 HEART 调用比心脚本："
        ).strip()
        if heart_confirmation != "HEART":
            print("未确认比心动作，程序停止，不调用比心脚本。")
            return 0

        # 03_example_heart.py initializes GalbotRobot itself. Release this
        # client first so the two scripts do not contend for the same SDK resources.
        shutdown_robot(robot)
        initialized = False
        run_heart_script()
        print("整个动作序列完成。")
        return 0

    except KeyboardInterrupt:
        print("\n检测到 Ctrl+C，正在请求底盘停止。")
        return 130
    except Exception as exc:
        print(f"执行失败: {exc}")
        return 1
    finally:
        if initialized:
            stop_base_with_retries(robot)
        try:
            if initialized:
                shutdown_robot(robot)
        except Exception as exc:
            print(f"SDK 资源释放异常: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
