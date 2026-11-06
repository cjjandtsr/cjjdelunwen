"""渲染图4(a)—(e)与图形摘要的三维画面，输出到 图表/v3/render/（已存在的跳过，--force 重渲染）。

python 图表/render_figures_v3.py                 # 用当前 Python（需 pip install bpy==4.2.0，Python 3.11）
python 图表/render_figures_v3.py --blender "C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
python 图表/render_figures_v3.py --quick         # 低分辨率快速预览

渲染完成后运行 python 图表/make_figures_v3.py --only 4 GA 合成带标注的成图。
任务选择与 make_figures_v3.FIG4_TASKS 一致：(a)瓶颈通道 T12 受阻、(b)U形陷阱 T30 受阻、(c)S形多障碍 T55 受阻、
(d)低密度前方偏置 T7 未受阻；(e)取 T55 起点的机体系点云；图形摘要取 T30 并叠加后训练策略第1次重复（到达）的执行路径。
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "render" / "render_task_scene.py"
OUT = HERE / "v3" / "render"
sys.path.insert(0, str(HERE))
from make_figures_v3 import FIG4_TASKS  # noqa: E402

JOBS = {
    "fig4_a": ["--mode", "scene", "--task", str(FIG4_TASKS["a"])],
    "fig4_b": ["--mode", "scene", "--task", str(FIG4_TASKS["b"])],
    "fig4_c": ["--mode", "scene", "--task", str(FIG4_TASKS["c"])],
    "fig4_d": ["--mode", "scene", "--task", str(FIG4_TASKS["d"])],
    "fig4_e": ["--mode", "cloud", "--task", str(FIG4_TASKS["c"]), "--aspect", "1.15"],
    "ga_scene": ["--mode", "scene", "--task", str(FIG4_TASKS["b"]), "--path", "rl_2f3f9914db78_u32", "1",
                 "--aspect", "1.1", "--no-line"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blender", default=None, help="Blender 可执行文件；不给则用当前 Python 的 bpy 模块")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--jobs", type=int, default=2, help="并行渲染数")
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    res, spp = ("700", "24") if a.quick else ("1400", "96")

    def run(name):
        out = OUT / f"{name}.png"
        if out.exists() and not a.force:
            print("skip", out); return 0
        args = JOBS[name] + ["--out", str(out), "--res", res, "--spp", spp]
        cmd = ([a.blender, "-b", "-P", str(SCRIPT), "--"] if a.blender else [sys.executable, str(SCRIPT)]) + args
        r = subprocess.run(cmd, capture_output=True, text=True)
        tail = "\n".join(l for l in r.stdout.splitlines() if l.startswith(("saved", "task", "cloud", "path")))
        print(f"[{name}] rc={r.returncode}\n{tail}")
        if r.returncode:
            print(r.stderr[-2000:])
        return r.returncode
    with ThreadPoolExecutor(a.jobs) as ex:
        rcs = list(ex.map(run, a.only or list(JOBS)))
    sys.exit(max(rcs) if rcs else 0)


if __name__ == "__main__":
    main()
