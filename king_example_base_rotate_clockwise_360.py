"""Rotate the Galbot G1 base clockwise by approximately 360 degrees.

This script targets Galbot SDK 1.8.1. It uses timed angular velocity, so the
actual angle is approximate and can be affected by acceleration and wheel slip.
Clockwise is defined as viewed from above the robot.
"""

import math
import time

from galbot_sdk.g1 import ControlStatus, GalbotRobot


ANGULAR_SPEED_RAD_S = 0.1
TEST_ANGLE_DEG = 15.0
TOTAL_ANGLE_DEG = 360.0

# This script assumes the usual right-hand convention for base_link: negative
# wz is clockwise when viewed from above. The 15-degree test verifies that
# assumption on the actual robot before the long rotation starts.
LINEAR_VELOCITY = [0.0, 0.0, 0.0]
CLOCKWISE_ANGULAR_VELOCITY = [0.0, 0.0, -ANGULAR_SPEED_RAD_S]


def wait_interruptibly(duration_s: float) -> None:
    """Wait in short intervals so Ctrl+C can be handled promptly."""
    deadline = time.monotonic() + duration_s
    while True:
        remaining_s = deadline - time.monotonic()
        if remaining_s <= 0.0:
            return
        time.sleep(min(0.1, remaining_s))


def stop_base_with_retries(robot: GalbotRobot, attempts: int = 3) -> bool:
    """Request a base stop, retrying briefly if the SDK reports failure."""
    for attempt in range(1, attempts + 1):
        status = robot.stop_base()
        if status == ControlStatus.SUCCESS:
            print("底盘停止成功。")
            return True
        print(f"底盘停止失败，第 {attempt}/{attempts} 次，状态: {status}")
        time.sleep(0.2)

    print("无法通过 SDK 确认底盘停止，请立即按实体急停按钮。")
    return False


def rotate_clockwise(robot: GalbotRobot, angle_deg: float, stage_name: str) -> None:
    """Command one timed clockwise rotation stage and then explicitly stop."""
    angle_rad = math.radians(angle_deg)
    duration_s = angle_rad / ANGULAR_SPEED_RAD_S

    print(
        f"{stage_name}: 顺时针 {angle_deg:.1f} 度，"
        f"角速度 {ANGULAR_SPEED_RAD_S:.2f} rad/s，"
        f"预计用时 {duration_s:.2f} 秒。"
    )
    status = robot.set_base_velocity(
        LINEAR_VELOCITY,
        CLOCKWISE_ANGULAR_VELOCITY,
        duration_s,
    )
    if status != ControlStatus.SUCCESS:
        raise RuntimeError(f"底盘速度指令下发失败，状态: {status}")

    wait_interruptibly(duration_s + 0.2)
    if not stop_base_with_retries(robot):
        raise RuntimeError("SDK 未能确认底盘已经停止")


def main() -> int:
    robot = GalbotRobot()
    initialized = False

    try:
        print("正在初始化 GalbotRobot...")
        if not robot.init():
            print("GalbotRobot 初始化失败，程序不会下发运动指令。")
            return 1
        initialized = True
        time.sleep(1.0)
        print("初始化成功。")

        print("\n运行前必须确认：")
        print("1. 机器人位于平整地面，周围及机械臂扫掠范围至少留出 2 米。")
        print("2. 机器人没有连接充电线或其他可能缠绕的线缆。")
        print("3. 机械臂处于紧凑、安全且不会碰撞周围物体的姿态。")
        print("4. 一名操作人员全程守在可用的实体急停按钮旁。")
        confirmation = input("全部确认后输入 ROTATE；输入其他内容将退出：").strip()
        if confirmation != "ROTATE":
            print("未收到完整安全确认，取消运动。")
            return 0

        print("机器人将在 3 秒后开始 15 度方向测试。")
        for seconds in (3, 2, 1):
            print(seconds)
            time.sleep(1.0)

        rotate_clockwise(robot, TEST_ANGLE_DEG, "方向测试")

        direction_ok = input(
            "从机器人上方向下看，刚才是否为顺时针旋转？输入 y 执行剩余 345 度："
        ).strip().lower()
        if direction_ok != "y":
            print("方向未确认，程序停止；不要直接修改符号后重试。")
            return 0

        remaining_angle_deg = TOTAL_ANGLE_DEG - TEST_ANGLE_DEG
        rotate_clockwise(robot, remaining_angle_deg, "正式旋转")
        print("360 度名义旋转完成。实际角度可能因轮胎打滑和加减速存在误差。")
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
            robot.request_shutdown()
            robot.wait_for_shutdown()
            robot.destroy()
            print("SDK 资源已释放。")
        except Exception as exc:
            print(f"SDK 资源释放异常: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
