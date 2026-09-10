# day1/code/example_joint_control.py
"""
模块 1.5 动手练习模板
需要修改此处：read_joint_groups、target_joint_groups、target_positions 和 max_speed 参数
"""

import time
from galbot_sdk.g1 import GalbotRobot, ControlStatus


def check_robot_safety():
    """安全确认：检查机器人是否满足执行条件"""
    # 运行前提示注意事项
    print(
        "注意：1）请确认机器人急停按钮已释放；"
        "2）请确认机器人前后左右无障碍物，避免发生意外。"
    )
    while True:
        key = (
            input("请确认急停已释放且周围无障碍物，是否继续执行？(y/n)：")
            .strip()
            .lower()
        )
        if key == "y":
            print("已确认，继续执行...")
            break
        if key == "n":
            print("未确认，程序退出。")
            exit(1)
        print("输入无效，请输入 'y' 或 'n'")


def main():
    # 获取并初始化 GalbotRobot 单例
    robot = GalbotRobot()
    if not robot.init():
        print("机器人初始化失败")
        return
    time.sleep(1)
    print("初始化成功")

    try:
        check_robot_safety()

        # ---------- 1. 读取当前关节角度 ----------
        print("\n=== Step 1: 读取当前关节角度 ===")
        # TODO: 修改此处 — 选择读取关节组（示例：["right_arm"]）
        read_joint_groups = ["right_arm"]
        if not read_joint_groups:
            print('请先修改 read_joint_groups，例如 ["right_arm"]')
            return

        current_positions = robot.get_joint_positions(
            joint_groups=read_joint_groups, joint_names=[]
        )
        print(f"读取关节组: {read_joint_groups}")
        print(f"当前关节角度: {current_positions}")

        print("\n=== 获取详细的关节状态信息 ===")
        read_joint_names = robot.get_joint_names(
            only_active_joint=True, joint_groups=read_joint_groups
        )
        current_states = robot.get_joint_states(
            joint_groups =read_joint_groups, joint_names=[]
        )
        for name, state in zip(read_joint_names, current_states):
            print(
                f"{name}: "
                f"position={state.position:.4f} rad, "
                f"velocity={state.velocity:.4f} rad/s, "
                f"acceleration={state.acceleration:.4f} rad/s^2, "
                f"effort={state.effort:.4f} N*m, "
                f"current={state.current:.4f} A"
            )

        # ---------- 2. 设置目标姿态 ----------
        print("\n=== Step 2: 设置目标姿态 ===")
        # TODO: 修改此处 — 目标关节组（示例：["right_arm"]）
        target_joint_groups = ["right_arm"]
        if not target_joint_groups:
            print('请先修改 target_joint_groups，例如 ["right_arm"]')
            return

        target_joint_names = robot.get_joint_names(
            only_active_joint=True, joint_groups=target_joint_groups
        )
        # 注意：joint_pos 顺序必须与 target_joint_groups 展开后的关节顺序一致
        # 例如仅控制 right_arm 时，对应 right_arm_joint1~7
        # TODO: 修改此处 — 根据 target_joint_groups 填写目标角度（弧度）
        target_positions = [-1.0,1.26,2.37,-0.81,-1.08,0.16,1]  # 示例：右臂 7 个关节 + 左臂 7 个关节
        if not target_positions:
            print("请先修改 target_positions（弧度）")
            return
        if len(target_positions) != len(target_joint_names):
            print(
                "目标角度数量与目标关节数量不一致："
                f"{len(target_positions)} != {len(target_joint_names)}"
            )
            print(f"目标关节顺序: {target_joint_names}")
            return

        print(f"目标角度设置为: {target_positions}")

        # TODO: 修改此处 — 尝试不同的 max_speed 值，观察速度变化
        # 建议值：0.05（慢速）~ 0.5（快速），超过 1.0 可能不安全
        max_speed = 0.1

        # TODO: 修改此处 — 分别设置为 True / False，观察阻塞与非阻塞区别
        is_blocking = True
        timeout_s = 30.0

        # ---------- 3. 执行运动 ----------
        print(
            f"\n=== Step 3: 执行运动 (max_speed={max_speed}, blocking={is_blocking}) ==="
        )
        mode_text = "阻塞模式" if is_blocking else "非阻塞模式"
        print(f"当前控制模式：{mode_text}")
        print("准备调用 set_joint_positions...")
        t0 = time.time()

        status = robot.set_joint_positions(
            joint_positions=target_positions,
            joint_groups=target_joint_groups,
            joint_names=[],
            is_blocking=is_blocking,
            speed_rad_s=max_speed,
            timeout_s=timeout_s,
        )
        elapsed = time.time() - t0
        print(f"set_joint_positions 已返回，耗时 {elapsed:.3f}s")

        if status != ControlStatus.SUCCESS:
            print(f"运动执行失败，状态: {status}")
            return

        if is_blocking:
            print("阻塞模式：运动已执行完成")
        else:
            print("非阻塞模式：命令已下发（不代表已经到位）")
            print("可等待一会后查看 Step 4 的角度结果")

        # ---------- 4. 验证结果 ----------
        print("\n=== Step 4: 验证结果 ===")
        time.sleep(2.0)
        final_positions = robot.get_joint_positions(
            joint_groups=target_joint_groups, joint_names=[]
        )
        print(f"目标关节组: {target_joint_groups}")
        print(f"目标关节角度: {target_positions}")
        print(f"运动后关节角度: {final_positions}")

    except Exception as e:
        print(f"发生异常: {e}")

    finally:
        # ---------- 5. 安全关闭 ----------
        print("\n=== 安全关闭 ===")
        robot.request_shutdown()
        robot.wait_for_shutdown()
        robot.destroy()
        print("资源已释放，程序结束")


if __name__ == "__main__":
    main()
