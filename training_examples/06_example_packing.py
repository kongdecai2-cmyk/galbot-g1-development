# day1/code/example_packing_pose.py
"""
示例：让 Galbot G1 进入装箱位姿

功能说明：
1. 先调节头部归位
2. 再依次调节左臂、右臂到装箱角度
3. 最后调节腿部归位（FAQ 强调：一定要先调节手臂，最后调节腿部）

位姿数据来源：troubleshooting/FAQ.md —— 第四节"关节相关问题"

关节组说明：
- head: 2个关节 (head_joint1=俯仰pitch, head_joint2=偏航yaw)
- left_arm: 7个关节 (left_arm_joint1~7)
- right_arm: 7个关节 (right_arm_joint1~7)
- leg: 5个关节 (leg_joint1~5)

装箱位姿参数：
- head: [0.0, 0.0]
- left_arm: [2.63, -1.5, -0.63, -2.07, -0.15, -0.74, 0.15]
- right_arm: [-2.63, 1.5, 0.63, 2.07, 0.15, 0.74, -0.15]
- leg: [0.06, 0.22, 0.14, 0.0, 0.0]
"""

import time
from galbot_sdk.g1 import GalbotRobot, ControlStatus


# ============================================================
# 装箱位姿（来自 FAQ.md）
# ============================================================

HEAD_PACKING = [0.0, 0.0]
LEFT_ARM_PACKING = [2.63, -1.5, -0.63, -2.07, -0.15, -0.74, 0.15]
RIGHT_ARM_PACKING = [-2.63, 1.5, 0.63, 2.07, 0.15, 0.74, -0.15]
LEG_PACKING = [0.06, 0.22, 0.14, 0.0, 0.0]

# --- 运动参数 ---
DEFAULT_SPEED = 0.2
DEFAULT_TIMEOUT = 40.0


def check_robot_safety():
    """安全确认：检查机器人是否满足执行条件"""
    print(
        "╔════════════════════════════════════════════════════════╗\n"
        "║  ⚠️  安全提醒                                          ║\n"
        "║  1）请确认机器人急停按钮已释放                          ║\n"
        "║  2）请确认机器人前后左右无障碍物，避免发生碰撞           ║\n"
        "║  3）调节期间发现轨迹异常，请随时拍下急停！               ║\n"
        "║  4）一定要先调节手臂，最后调节腿部                      ║\n"
        "╚════════════════════════════════════════════════════════╝"
    )
    while True:
        key = (
            input("请确认急停已释放且周围无障碍物，是否继续执行？(y/n)：")
            .strip()
            .lower()
        )
        if key == "y":
            print("✅ 已确认，继续执行...")
            break
        if key == "n":
            print("❌ 未确认，程序退出。")
            exit(1)
        print("输入无效，请输入 'y' 或 'n'")


def move_joints(
    robot: GalbotRobot,
    joint_groups: list,
    target_positions: list,
    speed: float = DEFAULT_SPEED,
    timeout: float = DEFAULT_TIMEOUT,
    description: str = "",
    retry: int = 3,
):
    """封装关节运动调用，支持自动重试"""
    if description:
        print(f"\n>>> {description}")
    print(f"    目标关节组: {joint_groups}")
    print(f"    目标角度: {[round(x, 3) for x in target_positions]}")

    for attempt in range(retry + 1):
        status = robot.set_joint_positions(
            target_positions,
            joint_groups,
            [],
            True,
            speed,
            timeout,
        )
        if status == ControlStatus.SUCCESS:
            print(f"    ✅ 运动执行成功")
            return True
        if attempt < retry:
            print(f"    ⚠️  运动失败，第 {attempt + 1} 次重试...")
            time.sleep(1)
        else:
            print(f"    ❌ 运动执行失败，状态: {status}")
    return False


def main():
    # ---------- 初始化机器人 ----------
    robot = GalbotRobot()
    if not robot.init():
        print("❌ 机器人初始化失败")
        return
    time.sleep(1)
    print("\n✅ 机器人初始化成功")

    try:
        check_robot_safety()

        # ---------- 启动控制器 ----------
        print("\n=== 启动关节控制器 ===")
        status = robot.start_controller("all")
        print(f"启动所有控制器状态: {status}")
        time.sleep(1)

        # 给用户一个确认机会
        print("\n" + "=" * 50)
        print("📋 即将执行以下动作序列（装箱位姿）：")
        print("  1. 🦿 头部归位")
        print("  2. 🦾 左臂归位")
        print("  3. 🦾 右臂归位")
        print("  4. 🦿 腿部归位（最后调节腿部！）")
        print("=" * 50)
        confirm = input("\n确认开始执行？(y/n)：").strip().lower()
        if confirm != "y":
            print("用户取消，程序退出。")
            return

        # ========================================================
        # 动作 1：头部归位
        # ========================================================
        print("\n" + "=" * 50)
        print("🦿 动作 1：头部归位")
        print("=" * 50)
        if not move_joints(
            robot,
            joint_groups=["head"],
            target_positions=HEAD_PACKING,
            description="头部归位（head_q: 0 0）",
        ):
            print("⚠️ 头部归位失败，继续执行后续动作")
        time.sleep(0.5)

        # ========================================================
        # 动作 2：左臂归位
        # ========================================================
        print("\n" + "=" * 50)
        print("🦾 动作 2：左臂归位")
        print("=" * 50)
        if not move_joints(
            robot,
            joint_groups=["left_arm"],
            target_positions=LEFT_ARM_PACKING,
            description="左臂归位（left_q: 2.63 -1.5 -0.63 -2.07 -0.15 -0.74 0.15）",
        ):
            print("⚠️ 左臂归位失败，继续执行后续动作")
        time.sleep(0.5)

        # ========================================================
        # 动作 3：右臂归位
        # ========================================================
        print("\n" + "=" * 50)
        print("🦾 动作 3：右臂归位")
        print("=" * 50)
        if not move_joints(
            robot,
            joint_groups=["right_arm"],
            target_positions=RIGHT_ARM_PACKING,
            description="右臂归位（right_q: -2.63 1.5 0.63 2.07 0.15 0.74 -0.15）",
        ):
            print("⚠️ 右臂归位失败，继续执行后续动作")
        time.sleep(0.5)

        # ========================================================
        # 动作 4：腿部归位（一定要先调节手臂，最后调节腿部）
        # ========================================================
        print("\n" + "=" * 50)
        print("🦿 动作 4：腿部归位")
        print("=" * 50)
        if not move_joints(
            robot,
            joint_groups=["leg"],
            target_positions=LEG_PACKING,
            description="腿部归位（leg5_q: 0.06 0.22 0.14 0 0）",
        ):
            print("⚠️ 腿部归位失败")
        time.sleep(0.5)

        print("\n" + "=" * 50)
        print("🎉 装箱位姿设置完毕！")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 发生异常: {e}")

    finally:
        # ---------- 安全关闭 ----------
        print("\n=== 安全关闭 ===")
        robot.request_shutdown()
        robot.wait_for_shutdown()
        robot.destroy()
        print("资源已释放，程序结束")


if __name__ == "__main__":
    main()
