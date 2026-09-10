import json
import time
from typing import List
from galbot_sdk.g1 import GalbotRobot, ControlStatus


def check_robot_safety():
    """安全确认：检查机器人是否满足执行条件"""
    print(
        "注意：1）请确认机器人急停按钮已释放；"
        "2）请确认机器人前后左右无障碍物，避免发生意外。"
    )
    while True:
        key = input("请确认急停已释放且周围无障碍物，是否继续执行？(y/n)：").strip().lower()
        if key == "y":
            print("已确认，继续执行...")
            break
        if key == "n":
            print("未确认，程序退出。")
            exit(1)
        print("输入无效，请输入 'y' 或 'n'")


# TODO(修改此处): 示教脚本输出文件路径（来自 example_teach_pick_place_pose.py）
TEACH_JSON = "day1/code/teach_grasp_right_arm.json"


def set_gripper(
    robot: GalbotRobot,
    gripper_name: str,
    width_m: float,
    velocity_mps: float,
    effort: float,
    is_blocking: bool = True,
) -> None:
    status = robot.set_gripper_command(
        end_effector=gripper_name,
        width_m=width_m,
        velocity_mps=velocity_mps,
        effort=effort,
        is_blocking=is_blocking,
    )
    if status != ControlStatus.SUCCESS:
        raise RuntimeError(f"夹爪控制失败: status={status}")


def move_joint_positions(
    robot: GalbotRobot,
    arm_group: str,
    joint_names: List[str],
    target_joint_pos: List[float],
    timeout_s: float,
    speed_rad_s: float,
) -> None:
    status = robot.set_joint_positions(
        joint_positions=target_joint_pos,
        joint_groups=[arm_group],
        joint_names=joint_names,
        is_blocking=True,
        speed_rad_s=speed_rad_s,
        timeout_s=timeout_s,
    )
    if status != ControlStatus.SUCCESS:
        raise RuntimeError(f"关节运动失败: status={status}")


def main():
    check_robot_safety()

    with open(TEACH_JSON, "r", encoding="utf-8") as f:
        teach = json.load(f)

    # teach 文件由 example_teach_pick_place_pose.py 生成
    arm_group = teach["arm_group"]
    gripper_name = teach["gripper_name"]
    joint_names = teach["joint_names"]
    start_joint_pos = teach["start_joint_pos"]
    pregrasp_joint_pos = teach["pregrasp_joint_pos"]
    grasp_joint_pos = teach["grasp_joint_pos"]
    preplace_joint_pos = teach["preplace_joint_pos"]
    place_joint_pos = teach["place_joint_pos"]

    # 使用示教脚本中的夹爪参数作为默认值
    meta = teach.get("meta", {})
    teach_open_width_m = meta.get("open_width_m", 0.08)
    teach_close_width_m = meta.get("close_width_m", 0.02)
    gripper_speed_mps = meta.get("gripper_speed_mps", 0.03)
    effort = meta.get("effort", meta.get("gripper_effort", 25))

    # TODO(修改此处): 夹爪回放参数
    open_width_m = teach_open_width_m
    close_width_margin_m = 0.003  # 回放时在示教抓取宽度基础上略微减小，提升夹稳概率
    close_width_m = max(0.0, teach_close_width_m - close_width_margin_m)

    # TODO(修改此处): 关节运动参数
    timeout_s = 15.0
    move_speed_rad_s = 0.2

    robot = GalbotRobot()
    if not robot.init():
        print("GalbotRobot 初始化失败")
        return

    time.sleep(1)
    print("初始化成功")
    print(f"已加载示教文件: {TEACH_JSON}")
    print(f"机械臂: {arm_group}, 夹爪: {gripper_name}")
    print(f"示教打开宽度 open_width_m: {teach_open_width_m}")
    print(f"示教抓取宽度 close_width_m: {teach_close_width_m}")
    print(f"回放抓取宽度 close_width_m: {close_width_m}")

    try:
        print("[Step 1] 夹爪打开（准备抓取）")
        set_gripper(robot, gripper_name, open_width_m, gripper_speed_mps, effort)

        print("[Step 2] 运动到起始位置")
        move_joint_positions(
            robot, arm_group, joint_names, start_joint_pos, timeout_s, move_speed_rad_s
        )

        print("[Step 3] 运动到预抓取位置")
        move_joint_positions(
            robot, arm_group, joint_names, pregrasp_joint_pos, timeout_s, move_speed_rad_s
        )

        print("[Step 4] 运动到抓取位置")
        move_joint_positions(
            robot, arm_group, joint_names, grasp_joint_pos, timeout_s, move_speed_rad_s
        )

        print("[Step 5] 关闭夹爪（执行抓取）")
        set_gripper(robot, gripper_name, close_width_m, gripper_speed_mps, effort)

        print("[Step 6] 抬起回到预抓取位置")
        move_joint_positions(
            robot, arm_group, joint_names, pregrasp_joint_pos, timeout_s, move_speed_rad_s
        )

        print("[Step 7] 运动到预放置位置")
        move_joint_positions(
            robot, arm_group, joint_names, preplace_joint_pos, timeout_s, move_speed_rad_s
        )

        print("[Step 8] 运动到放置位置")
        move_joint_positions(
            robot, arm_group, joint_names, place_joint_pos, timeout_s, move_speed_rad_s
        )

        print("[Step 9] 打开夹爪（执行释放）")
        set_gripper(robot, gripper_name, open_width_m, gripper_speed_mps, effort)

        print("[Step 10] 抬起回到预放置位置")
        move_joint_positions(
            robot, arm_group, joint_names, preplace_joint_pos, timeout_s, move_speed_rad_s
        )

        print("[Step 11] 回到起始位置")
        move_joint_positions(
            robot, arm_group, joint_names, start_joint_pos, timeout_s, move_speed_rad_s
        )

        print("固定位置 Pick&Place 流程执行完成。")

    except Exception as e:
        print(f"执行异常: {e}")
    finally:
        robot.request_shutdown()
        robot.wait_for_shutdown()
        robot.destroy()
        print("资源已释放")


if __name__ == "__main__":
    main()
