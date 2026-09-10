#!/usr/bin/env python
"""LIBERO 데모 실행기.

예시:
  python run_demo.py --list                       # 태스크 목록
  python run_demo.py --suite libero_spatial --task 0 --gui
  python run_demo.py --suite libero_object --task 3 --video out.mp4
"""
import argparse, numpy as np

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--suite", default="libero_spatial",
                   choices=["libero_spatial", "libero_object", "libero_goal",
                            "libero_90", "libero_10"])
    p.add_argument("--task", type=int, default=0)
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--gui", action="store_true", help="MuJoCo 창 띄우기")
    p.add_argument("--video", default=None, help="mp4로 저장할 경로")
    p.add_argument("--list", action="store_true", help="태스크 목록만 출력")
    args = p.parse_args()

    from libero.libero import benchmark, get_libero_path
    from libero.libero.envs.env_wrapper import ControlEnv, OffScreenRenderEnv

    suite = benchmark.get_benchmark_dict()[args.suite]()
    if args.list:
        for i in range(suite.n_tasks):
            print(f"[{i:2d}] {suite.get_task(i).language}")
        return

    task = suite.get_task(args.task)
    bddl = f"{get_libero_path('bddl_files')}/{task.problem_folder}/{task.bddl_file}"
    print(f"[{args.suite} #{args.task}] {task.language}")

    if args.gui:
        env = ControlEnv(bddl_file_name=bddl, has_renderer=True,
                         has_offscreen_renderer=False, use_camera_obs=False,
                         render_camera="frontview")
    else:
        env = OffScreenRenderEnv(bddl_file_name=bddl,
                                 camera_heights=256, camera_widths=256)

    env.seed(0)
    env.reset()
    env.set_init_state(suite.get_task_init_states(args.task)[0])

    frames = []
    for _ in range(args.steps):
        # 여기에 정책(policy)이 들어갑니다. 지금은 무작위 행동.
        action = np.random.uniform(-0.3, 0.3, 7)
        obs, reward, done, info = env.step(action)
        if args.gui:
            env.env.render()
        elif args.video:
            frames.append(obs["agentview_image"][::-1])
        if done:
            print("태스크 성공!")
            break

    if args.video and frames:
        import imageio
        imageio.mimsave(args.video, frames, fps=20)
        print(f"저장됨: {args.video}")
    env.close()

if __name__ == "__main__":
    main()
