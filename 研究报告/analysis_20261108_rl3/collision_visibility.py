"""Was the obstacle that is eventually hit inside the depth camera's horizontal field of view before impact?
Camera (diffusion_policy_3d/model/common/synth_pointcloud.py): HFOV 60 deg, far 10 m, looking along body x (yaw).
Approximation: obstacle 'in view' at a decision if the bearing from the drone to the obstacle's nearest horizontal point
lies within +-30 deg of yaw and that point is within 10 m (vertical FOV ignored; obstacles are tall prisms).
Also reports the angle between flight direction (executed segment) and yaw at impact.
Usage: python3 -I collision_visibility.py <project-repo-root> <traces-root> bc P6 P9"""
import json, sys, os, ast, math, collections
repo, root = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(repo, 'Improved-3D-Diffusion-Policy'))
from diffusion_policy_3d.env.collision_geom import segment_obstacle_collision, ObstacleSpec
TH = 0.1 + 2e-3
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def nearest_xy(o, p):
    if o['shape'] == 'cylinder':
        dx, dy = p[0] - o['x'], p[1] - o['y']; r = math.hypot(dx, dy) or 1e-9
        return (o['x'] + dx / r * o['radius'], o['y'] + dy / r * o['radius'])
    c, s = math.cos(-o['yaw']), math.sin(-o['yaw']); lx = (p[0] - o['x']) * c - (p[1] - o['y']) * s; ly = (p[0] - o['x']) * s + (p[1] - o['y']) * c
    lx = max(-o['size_x'] / 2, min(o['size_x'] / 2, lx)); ly = max(-o['size_y'] / 2, min(o['size_y'] / 2, ly))
    c, s = math.cos(o['yaw']), math.sin(o['yaw']); return (o['x'] + lx * c - ly * s, o['y'] + lx * s + ly * c)
def in_view(o, pos, yaw):
    q = nearest_xy(o, pos); d = math.hypot(q[0] - pos[0], q[1] - pos[1])
    if d < 1e-6: return True
    return d <= 10.0 and abs(wrap(math.atan2(q[1] - pos[1], q[0] - pos[0]) - yaw)) <= math.radians(30)
for pol in sys.argv[3:]:
    d = os.path.join(root, pol, 'traces'); vis = collections.Counter(); mis = []; n = 0
    for f in sorted(os.listdir(d)):
        L = [json.loads(l) for l in open(os.path.join(d, f))]
        s, e = L[0], L[-1]
        if e['done_reason'] != 'collision': continue
        task = s['task'] if isinstance(s['task'], dict) else ast.literal_eval(s['task'])
        g = task['goal_pos']; T = [t for t in L[1:] if t.get('type') == 'transition']
        if min(math.dist(q, g) for t in T for q in t['executed_path']) < 1.0: continue   # 1 m success, not a failure
        obs = [ObstacleSpec.from_dict(o) for o in s['geometry']]; byname = {o['name']: o for o in s['geometry']}
        last = T[-1]['executed_path']; name = None
        for a, b in zip(last[:-1], last[1:]):
            h = segment_obstacle_collision(a, b, obs, TH)
            if h: name = h[1]; break
        if name is None: continue
        n += 1; o = byname[name]
        for back in (1, 2, 3, 4):
            j = len(T) - 1 - back
            if j >= 0 and in_view(o, T[j]['pre_state']['position'], T[j]['pre_state']['yaw']): vis[back] += 1
        seen_any = any(in_view(o, t['pre_state']['position'], t['pre_state']['yaw']) for t in T[:-1])
        vis['ever_before_impact'] += seen_any
        a, b = last[0], last[-1]; heading = math.atan2(b[1] - a[1], b[0] - a[0])
        mis.append(abs(math.degrees(wrap(heading - T[-1]['pre_state']['yaw']))))
    mis.sort()
    print('== %s collision failures with identified obstacle: %d' % (pol, n))
    print('  hit obstacle in camera view at 1/2/3/4 decisions before impact: %s' % ' / '.join('%d (%.0f%%)' % (vis[k], 100 * vis[k] / n) for k in (1, 2, 3, 4)))
    print('  ever in view before impact: %d (%.0f%%)' % (vis['ever_before_impact'], 100 * vis['ever_before_impact'] / n))
    print('  |flight direction - yaw| at impact: median %.0f deg, >30 deg: %d (%.0f%%), >60 deg: %d (%.0f%%)' % (
        mis[len(mis) // 2], sum(x > 30 for x in mis), 100 * sum(x > 30 for x in mis) / n, sum(x > 60 for x in mis), 100 * sum(x > 60 for x in mis) / n))
