# Galbot G1 Project Handoff

Last updated: 2026-09-10

## Purpose

This document is a self-contained handoff for a collaborator or a new GPT working on this Galbot G1 project. It summarizes the known environment, verified results, safety limits, local conventions, and the current state of the code.

Read this document before proposing code changes, running robot code, changing SDK versions, or giving the user commands.

## Required Files To Hand Off

Share the complete project directory, not this document alone. The minimum set is:

- `PROJECT_HANDOFF.md`: this summary.
- `README.md`: repository entry point for human collaborators and GPTs.
- `AGENTS.md`: project behavior and teaching rules.
- `GALBOT_PROJECT_MEMORY.md`: detailed historical knowledge and user preferences.
- `GALBOT_SDK_1_8_1_REFERENCE.md`: structured, page-referenced knowledge base for the supplied SDK 1.8.1 PDF, including API and safety interpretation.
- `Galbot_SDK_G1_1.8.1SDK、API开发文档.pdf`: the supplied 589-page source PDF; read it for original context after the structured reference, not as a default execution guide.
- `king_example_base_rotate_clockwise_360.py`: verified rotation script.
- `galbot_forward_left_forward_heart.py`: verified-upload, real-robot-tested sequence script.
- `docs/RESOURCES.md`: official and supplemental resource links with version caveats.
- `training_examples/`: copies of the seven supplied training scripts, `01` through `07`.
- `SHA256SUMS.txt`: SHA-256 integrity manifest for all delivered Markdown, Python source, and PDF files; the manifest does not include its own hash.

Expected desktop handoff layout:

```text
银河机器人开发_交接_2026-09-10/
  AGENTS.md
  README.md
  GALBOT_PROJECT_MEMORY.md
  GALBOT_SDK_1_8_1_REFERENCE.md
  Galbot_SDK_G1_1.8.1SDK、API开发文档.pdf
  PROJECT_HANDOFF.md
  galbot_forward_left_forward_heart.py
  king_example_base_rotate_clockwise_360.py
  SHA256SUMS.txt
  docs/
    RESOURCES.md
  training_examples/
    01_example_sdk_check.py
    02_example_joint_control.py
    03_example_heart.py
    04_example_teach_pick_place_pose.py
    05_example_pick_place_fixed.py
    06_example_packing.py
    07_example_whole_body_reset_zero_odom.py
```

The training examples are preserved as supplied reference material. They are not approved to run in numeric order and are not a substitute for the safety rules in this document.

The collaboration target confirmed by the user is a private GitHub repository named `kongdecai2-cmyk/galbot-g1-development`. Before claiming publication, verify the remote URL, branch, commit, repository visibility and uploaded file list. A local commit alone is not proof that collaborators can clone the repository.

Never include passwords, SSH private keys, authorization tokens, device serial numbers, or default vendor credentials in the handoff.

## Bootstrap Instructions For Another GPT

Use this opening instruction in a new GPT task:

```text
This is a Galbot G1 real-robot project. Read README.md first. Before answering or modifying anything, read PROJECT_HANDOFF.md, AGENTS.md, and GALBOT_PROJECT_MEMORY.md completely. For SDK/API, deployment, mapping, navigation, sensor, planning, or troubleshooting questions, also read the relevant sections of GALBOT_SDK_1_8_1_REFERENCE.md. Treat robot motion as safety-critical. Verify changing facts rather than relying on old notes. Explain every action to a beginner: what it does, why it is needed, expected output, and risk. Distinguish verified facts from assumptions. Do not record or request passwords, private keys, or tokens.
```

The project files are written in Chinese because the user is a Chinese-speaking beginner. Keep future explanations in Chinese unless the user asks otherwise.

## Verified Environment

These facts came from user-provided terminal screenshots:

- Development PC: Windows with VS Code Remote SSH.
- PC and robot are connected to the same Wi-Fi router.
- SSH host: `192.168.102.49` on the private LAN.
- SSH user: `galbot`.
- Robot host name: `galbot-echo`.
- Personal robot script directory: `/userdata/KDC`.
- The `galbot` user has write permission to `/userdata/KDC`.
- Robot Python shown in VS Code: Python 3.8.10.
- SDK compatibility command reported:
  - SDK: `1.8.1`
  - required GBS: `GBS_1.16.x`
  - installed GBS: `GBS_1.16.0.2.rc88`
  - result: `MATCH`

The SDK prints that 1.9.1 is available. Do not upgrade: the installed 1.8.1 SDK is currently matched to the robot GBS 1.16.x system.

Unknown and therefore not safe to assume:

- Exact G1 hardware revision.
- Installed end effectors: grippers, suction cups, dexterous hands, or a mixture.
- Map, localization, navigation, battery and charging state.
- Current workspace conditions and emergency-stop training status.

## Official Sources And Documentation Quality

- Official GitHub organization: https://github.com/GalaxyGeneralRobotics
- SDK repository: https://github.com/GalaxyGeneralRobotics/GalbotSDK
- SDK 1.8.1 tag: https://github.com/GalaxyGeneralRobotics/GalbotSDK/releases/tag/V1.8.1
- Current online documentation: https://developer.galbot.com/docs/SDK/1.9.1/g1/zh/
- G1 manual: https://developer.galbot.com/docs/g1/2.2.4/zh/g1

The supplied 589-page PDF at `E:\WXWork\1688856602736104\Cache\File\2026-09\Galbot_SDK_G1_1.8.1SDK、API开发文档.pdf` is a third-party cached export of official web documentation. It is useful for SDK 1.8.1 APIs but is not a signed vendor release. Treat its stale deployment instructions and licensing page with caution.

## Safety Rules

Robot motion is safety-critical. The following rules are non-negotiable:

- A physically reachable, tested emergency-stop button and an assigned watcher are required for motion tests.
- Clear the base and arm sweep area before motion. Do not rely on a program prompt as an actual safety interlock.
- Wireless disconnection, closing VS Code, and Ctrl+C are not reliable emergency stops.
- Do not casually disable firewalls, use `chmod 777`, modify HPU/XCU network settings, release joint limits, modify motor/controller configuration, or restart low-level services.
- Do not start with high-frequency `set_joint_commands`, collision checks disabled, dual-arm demonstrations, fixed-path pick-and-place, packing, or whole-body reset scripts.
- A successful SDK status confirms that a command was accepted or completed at the software interface. It does not prove that the real-world trajectory was collision-free or geometrically accurate.
- `request_shutdown()` releases SDK resources; it does not place the robot into a safe physical pose.

## SDK Model

Main SDK modules:

- `GalbotRobot`: robot initialization, joints, base, grippers/suction cups, sensors and robot status.
- `GalbotMotion`: FK/IK, planning, collision checks, obstacles and tools.
- `GalbotNavigation`: localization, reachability, navigation and navigation status.
- `GalbotPerception`: model initialization, inference and result access.

Known G1 2.2 joint groups from documentation: `head` has 2 joints, `leg` has 5, `left_arm` has 7 and `right_arm` has 7. Do not assume the exact end-effector configuration.

## Mandatory File Transfer Workflow

For every Windows-to-robot script or configuration transfer:

1. On Windows PowerShell, calculate source SHA-256:

```powershell
Get-FileHash -LiteralPath "<local file path>" -Algorithm SHA256
```

2. Upload from Windows PowerShell, not the remote robot terminal:

```powershell
scp -p "<local file path>" galbot@192.168.102.49:/userdata/KDC/
```

3. On the robot, calculate destination SHA-256:

```bash
sha256sum /userdata/KDC/<file name>
```

4. Compare hashes character-for-character, ignoring case. Do not call the transfer successful until they match.

5. For Python scripts, check syntax without running the program:

```bash
cd /userdata/KDC
python3 -m py_compile <file name>
```

`py_compile` checks syntax only. It does not call `main()`, initialize the robot, or command motion.

## Existing Training Scripts

The user supplied seven scripts originally from `C:\Users\ASUS\Desktop\银河\`. Treat their names as hints, not proof of safety.

| File | Function | Risk |
| --- | --- | --- |
| `01_example_sdk_check.py` | Initializes SDK and reads active joint names; no explicit motion command. | Low |
| `02_example_joint_control.py` | Reads and commands a hard-coded right-arm pose. | Medium-high |
| `03_example_heart.py` | Moves both arms into a heart pose and restores them. | High |
| `04_example_teach_pick_place_pose.py` | Manually teaches and records a right-arm pick/place sequence. | High |
| `05_example_pick_place_fixed.py` | Replays a fixed taught pick/place sequence. | Very high |
| `06_example_packing.py` | Moves head, arms and leg into a packing pose. | Very high |
| `07_example_whole_body_reset_zero_odom.py` | Calls whole-body and base reset. | Very high |

Noted issues:

- Script 02 has a comment that claims both arms but actually commands only seven right-arm values.
- Script 03 says it displays the pose for 15 seconds, but the code waits only 5 seconds.
- Script 04 produces a relative JSON path; its output location depends on the run directory.
- Script 05 has no perception or scene validation; it is only valid for an unchanged taught scene.
- Script 06 retries failures and may continue after a failed step, which is unsafe for maintenance/packing use.
- Script 07 defines joint/base targets that it does not use, initializes `GalbotMotion` without using it, and lacks robust `try/finally` cleanup.

## Verified Custom Rotation Script

File: `king_example_base_rotate_clockwise_360.py`

Purpose: rotate the base clockwise by a nominal 360 degrees.

API basis verified against SDK 1.8.1 documentation:

- `set_base_velocity(linear_velocity, angular_velocity, duration_s)` commands base linear and angular velocity for a duration with an automatic stop.
- `stop_base()` requests a base stop.

Design:

- Uses zero linear velocity and angular velocity `[0.0, 0.0, -0.1]` rad/s.
- The negative `wz` direction assumes the common base-link right-hand convention; this is not treated as a vendor-verified sign convention.
- It performs a 15-degree test first, stops, then requires user confirmation before the remaining 345 degrees.
- It asks for the literal `ROTATE` before motion, uses a three-second countdown, checks `ControlStatus.SUCCESS`, attempts `stop_base()` up to three times, and stops again in `finally`.
- A full rotation is calculated by velocity times duration: 15 degrees takes about 2.62 seconds; 345 degrees takes about 60.21 seconds.

This is open-loop control. It cannot prove physical 360-degree accuracy because wheel slip, acceleration and floor conditions introduce error. A future closed-loop version should use verified odometry/IMU feedback and a safe tolerance, not simply increase speed or repeat rotations.

Validation and run record:

- Local file SHA-256 and robot file SHA-256 matched: `D60E04ED777818E3945B8D56486152C44EA0A7936ABAAED3D14D12359BF4C92C`.
- The robot copy at `/userdata/KDC/king_example_base_rotate_clockwise_360.py` passed `python3 -m py_compile`.
- The user ran it on the real robot on 2026-09-10 with a cleared area and an emergency-stop watcher.
- Terminal logs showed successful initialization, successful 15-degree direction test, user confirmation, successful 345-degree stage, two successful `stop_base()` reports, and SDK cleanup.
- This proves the software command flow completed. It does not independently measure that the physical final angle was exactly 360 degrees.

## Recommended Next Work

Do not repeat the 360-degree motion simply to test it again. First determine whether the robot physically returned near its initial heading with a floor marker. Then create a read-only program to capture available IMU and/or odometry data before and after a small test turn.

For the broader learning path, proceed from read-only SDK status checks to small, low-speed, single-component motion. Only later move to motion planning with collision checks, manual teaching, fixed replay, perception and navigation.

## Collaboration Checklist

Before another developer or GPT runs or edits code:

1. Read `PROJECT_HANDOFF.md`, `AGENTS.md`, and `GALBOT_PROJECT_MEMORY.md`.
2. Confirm the SDK/GBS combination using `galbot_sdk check-version`; do not change versions merely because an update exists.
3. Confirm the active remote directory and the intended target file.
4. For a transferred file, complete SHA-256 source/destination comparison and Python syntax check.
5. For motion, confirm physical workspace, emergency stop, observer, robot pose, and the exact expected action.
6. Make one small, measurable change at a time and record results in `GALBOT_PROJECT_MEMORY.md`.
7. Use `docs/RESOURCES.md` as the link index, but revalidate online content before treating it as current.

## Information That Must Be Revalidated

- Robot IP address, SSH reachability and user permissions.
- SDK and GBS versions.
- Robot hardware/end-effector configuration.
- Battery, charger, controller state, floor condition, arm pose and nearby obstacles.
- Map/localization state before any navigation.
- Exact API signatures if changing the installed SDK tag or moving code to another robot.
