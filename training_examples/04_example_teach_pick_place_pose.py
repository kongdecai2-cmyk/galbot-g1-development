import json
import os
import time
from typing import List, Optional
from galbot_sdk.g1 import GalbotRobot, ControlStatus


def check_robot_safety():
    """安全确认：检查机器人是否满足执行条件"""
    # 运行前提示注意事项
    print(
        "注意：1）请确认机器人急停按钮已释放；"
        "2）请确认机器人前后左右无障碍物，避免发生意外。"
    )
    while True:
        key = input(
            "请确认急停已释放且周围无障碍物，是否继续执行？(y/n)："
        ).strip().lower()
        if key == "y":
            print("已确认，继续执行...")
            break
        if key == "n":
            print("未确认，程序退出。")
            exit(1)
        print("输入无效，请输入 'y' 或 'n'")


def wait_confirm(msg: str) -> Optional[bool]:
    while True:
        key = input(f"{msg} (y/n)：").strip().lower()
        if key in {"y", "n"}:
            return key == "y"
        print("检测到非 y/n 输入。")
        confirm_exit = input("是否确认退出采集流程？(y/n)：").strip().lower()
        if confirm_exit == "y":
            print("已确认退出采集流程。")
            return None
        if confirm_exit == "n":
            print("继续当前步骤，请重新输入 y 或 n。")
            continue
        print("输入无效，继续当前步骤，请重新输入 y 或 n。")


def set_gripper(robot: GalbotRobot, gripper_name: str, width_m: float, velocity_mps: float, effort: float) -> None:
    status = robot.set_gripper_command(
        end_effector=gripper_name,
        width_m=width_m,
        velocity_mps=velocity_mps,
        effort=effort,
        is_blocking=True,
    )
    if status != ControlStatus.SUCCESS:
        raise RuntimeError(f"夹爪控制失败: status={status}")


def move_arm_to_start_pose(
    robot: GalbotRobot,
    arm_group: str,
    start_joint_pos: List[float],
    timeout_s: float,
) -> None:
    joint_names = robot.get_joint_names(only_active_joint=True, joint_groups=[arm_group])
    if not joint_names:
        raise RuntimeError(f"未获取到 {arm_group} 的关节名")

    if len(start_joint_pos) != len(joint_names):
        raise RuntimeError(
            f"起始关节角长度不匹配: 期望 {len(joint_names)}，实际 {len(start_joint_pos)}"
        )

    status = robot.set_joint_positions(
        joint_positions=start_joint_pos,
        joint_groups=[arm_group],
        joint_names=[],
        is_blocking=True,
        speed_rad_s=0.2,
        timeout_s=timeout_s,
    )
    if status != ControlStatus.SUCCESS:
        raise RuntimeError(f"机械臂移动到起始点失败: status={status}")


def record_joint_positions(robot: GalbotRobot, arm_group: str) -> List[float]:
    pos = robot.get_joint_positions(joint_groups=[arm_group], joint_names=[])
    if not pos:
        raise RuntimeError(f"读取 {arm_group} 关节角失败")
    return pos


def main():
    # TODO(修改此处): 示教机械臂，可选 "left_arm" / "right_arm"
    arm_group = "right_arm"
    # TODO(修改此处): 示教文件输出路径
    output_json = "day1/code/teach_grasp_right_arm.json"

    # TODO(修改此处): 夹爪参数（用于示教确认）
    open_width_m = 0.09
    close_width_m = 0.065
    gripper_speed_mps = 0.03
    effort = 25
    timeout_s = 15.0
    # TODO(修改此处): 起始点关节角。当前先指定为全零关节角，后续可替换成更优起始姿态。
    custom_start_joint_pos = None  # 示例: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    gripper_name = "right_gripper" if arm_group == "right_arm" else "left_gripper"

    robot = GalbotRobot()
    if not robot.init():
        print("GalbotRobot 初始化失败")
        return
    time.sleep(1)
    print("初始化成功")

    try:
        check_robot_safety()

        print("\n========== 示教流程开始 ==========")
        print("目标：记录一组有效抓放示教数据（起始点/预抓取点/抓取点/预放置点/放置点）")
        print(f"当前机械臂：{arm_group}，夹爪：{gripper_name}")

        # 先将夹爪打开，便于后续抓取确认
        print("\n[准备] 打开夹爪到初始状态...")
        set_gripper(robot, gripper_name, open_width_m, gripper_speed_mps, effort)
        print("[准备] 夹爪已打开")

        attempt = 0
        while True:
            attempt += 1
            print(f"\n========== 第 {attempt} 次示教尝试 ==========")

            confirm = wait_confirm(
                "步骤1：将机械臂移动到起始点。是否执行"
            )
            if confirm is None:
                print("用户退出采集流程，程序结束。")
                return
            if not confirm:
                print("用户取消移动到起始点，程序结束。")
                return

            joint_names = robot.get_joint_names(only_active_joint=True, joint_groups=[arm_group])
            start_joint_pos_cmd = custom_start_joint_pos if custom_start_joint_pos is not None else [-2.0, 1.5, 0.6, 1.7, 0.0, 0.8, 0.0]
            move_arm_to_start_pose(robot, arm_group, start_joint_pos_cmd, timeout_s)
            start_joint_pos = record_joint_positions(robot, arm_group)
            print("已记录起始关节角（移动到起始点后）")
            print(f"起始关节角: {start_joint_pos}")

            print("\n步骤2：请按住机械臂末端的绿色示教按钮并持续按下，")
            print("然后拖动机械臂到抓取目标正上方约10cm（预抓取位置）。")
            confirm = wait_confirm("完成拖动后，是否确认记录“预抓取位置”")
            if confirm is None:
                print("用户退出采集流程，程序结束。")
                return
            if not confirm:
                print("用户未确认预抓取位置，重新开始本次示教。")
                continue

            pregrasp_joint_pos = record_joint_positions(robot, arm_group)
            print(f"已记录预抓取关节角: {pregrasp_joint_pos}")

            print("\n步骤3：继续按住绿色示教按钮，将机械臂拖动到最终抓取位置。")
            confirm = wait_confirm("完成拖动后，是否确认记录“抓取位置”")
            if confirm is None:
                print("用户退出采集流程，程序结束。")
                return
            if not confirm:
                print("用户未确认抓取位置，重新开始本次示教。")
                continue

            grasp_joint_pos = record_joint_positions(robot, arm_group)
            print(f"已记录抓取关节角: {grasp_joint_pos}")

            print("\n步骤4：接下来将执行夹爪闭合（起始位置夹爪应为打开状态）。")
            confirm = wait_confirm("是否确认执行夹爪闭合")
            if confirm is None:
                print("用户退出采集流程，程序结束。")
                return
            if not confirm:
                print("用户取消夹爪闭合，重新开始本次示教。")
                continue

            set_gripper(robot, gripper_name, close_width_m, gripper_speed_mps, effort)
            print("夹爪闭合完成。")

            print("\n步骤5：请继续按住绿色示教按钮，将机械臂拖动到放置目标正上方约10cm（预放置位置）。")
            confirm = wait_confirm("完成拖动后，是否确认记录“预放置位置”")
            if confirm is None:
                print("用户退出采集流程，程序结束。")
                return
            if not confirm:
                print("用户未确认预放置位置，重新开始本次示教。")
                continue

            preplace_joint_pos = record_joint_positions(robot, arm_group)
            print(f"已记录预放置关节角: {preplace_joint_pos}")

            print("\n步骤6：继续按住绿色示教按钮，将机械臂拖动到最终放置位置。")
            confirm = wait_confirm("完成拖动后，是否确认记录“放置位置”")
            if confirm is None:
                print("用户退出采集流程，程序结束。")
                return
            if not confirm:
                print("用户未确认放置位置，重新开始本次示教。")
                continue

            place_joint_pos = record_joint_positions(robot, arm_group)
            print(f"已记录放置关节角: {place_joint_pos}")

            print("\n步骤7：接下来将执行夹爪张开（模拟放置释放）。")
            confirm = wait_confirm("是否确认执行夹爪张开")
            if confirm is None:
                print("用户退出采集流程，程序结束。")
                return
            if not confirm:
                print("用户取消夹爪张开，重新开始本次示教。")
                continue

            set_gripper(robot, gripper_name, open_width_m, gripper_speed_mps, effort)
            print("夹爪张开完成。")

            confirm = wait_confirm("步骤8：请确认本次抓放示教是否成功并保存")
            if confirm is None:
                print("用户退出采集流程，程序结束。")
                return
            if confirm:
                record = {
                    "arm_group": arm_group,
                    "gripper_name": gripper_name,
                    "joint_names": joint_names,
                    "start_joint_pos": start_joint_pos,
                    "pregrasp_joint_pos": pregrasp_joint_pos,
                    "grasp_joint_pos": grasp_joint_pos,
                    "preplace_joint_pos": preplace_joint_pos,
                    "place_joint_pos": place_joint_pos,
                    "meta": {
                        "open_width_m": open_width_m,
                        "close_width_m": close_width_m,
                        "gripper_speed_mps": gripper_speed_mps,
                        "effort": effort,
                        "record_time_s": int(time.time()),
                    },
                }
                os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)
                print("\n抓放示教成功，数据已保存：")
                print(output_json)
                break

            print("本次抓放示教未通过确认，不记录数据。将重新开始示教流程。")

    except Exception as e:
        print(f"执行异常: {e}")
    finally:
        robot.request_shutdown()
        robot.wait_for_shutdown()
        robot.destroy()
        print("资源已释放")


if __name__ == "__main__":
    main()
