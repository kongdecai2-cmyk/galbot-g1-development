"""
example_sdk检查脚本

用途：
1. 验证 galbot_sdk Python 包可正常导入
2. 验证 GalbotRobot 可初始化
3. 验证可读取基础关节信息
"""

from galbot_sdk.g1 import GalbotRobot


def main():
    robot = GalbotRobot()
    print("开始 example_sdk 检查...")

    try:
        if not robot.init():
            print("SDK 检查失败：robot.init() 返回 False")
            return 1

        joint_names = robot.get_joint_names(only_active_joint=True, joint_groups=[])
        print("SDK 检查成功：机器人初始化成功，接口可调用。")
        print(f"读取到激活关节数量: {len(joint_names)}")
        if joint_names:
            print("前 10 个关节名:", joint_names[:10])
        return 0
    except Exception as exc:
        print(f"SDK 检查失败：{exc}")
        return 1
    finally:
        try:
            robot.request_shutdown()
            robot.wait_for_shutdown()
            robot.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
