"""P2 descriptive results from archived evaluations; no policy execution.

Run with the project's document Python runtime. Figures use executed paths only.
The audit JSON supplies full-set statistics; selected raw paths are independently
checked against its length, elapsed-time and terminal-distance measurements.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import sys
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import pypdfium2 as pdfium

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent


def paper_p3():
    """Render verified P3 data; keep the existing P2 entry and outputs intact."""
    source=ROOT/'论文/研究报告/2026-10-21_论文P3与有限任务评价独立验收数据.json'
    data=json.loads(source.read_text(encoding='utf-8'))
    run=ROOT/data['source_root']/'results'
    states=data['p3_states']
    frozen=json.loads((run/'recovery/frozen_bank.json').read_text(encoding='utf-8'))
    lookup={s['id']:s for s in frozen['states']}
    assert len(states)==24 and sum(s['bc_reached'] for s in states)==46
    assert sum(s['rl_reached'] for s in states)==41
    colors=['#23688d','#b64d35']
    hashes={str(source.relative_to(ROOT)):hashlib.sha256(source.read_bytes()).hexdigest()}
    def txt(c,x,y,s,size=10):
        c.setFont('Helvetica',size);c.setFillColor(HexColor('#263746'));c.drawString(x,y,str(s))
    def ln(c,points,color,width=1,dash=False):
        c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.setDash(4,2) if dash else c.setDash()
        p=c.beginPath();p.moveTo(*points[0])
        for q in points[1:]:p.lineTo(*q)
        c.drawPath(p);c.setDash()
    def save(c,name):
        c.save();pdf=pdfium.PdfDocument(str(OUT/(name+'.pdf')))
        pdf[0].render(scale=2).to_pil().save(OUT/(name+'.png'));pdf.close()
    name='figure_04_same_state_arrivals'
    c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=(720,475))
    txt(c,28,448,'Safe arrival from the same state: all 24 frozen states',16)
    txt(c,28,427,'BC: 46/120; DPPO u32: 41/120. Paired gains: 16; losses: 21.',11)
    for panel in range(2):
        base=30+panel*355;x0=base+108;w=175
        for tick in range(6):
            x=x0+tick*w/5;ln(c,[(x,75),(x,395)],'#e1e5e8',.6);txt(c,x-3,57,tick,10)
        txt(c,base+99,38,'Arrivals / 5 continuations',10)
        for j,s in enumerate(states[panel*12:(panel+1)*12]):
            y=384-j*26;a=x0+s['bc_reached']*w/5;b=x0+s['rl_reached']*w/5
            txt(c,base,y-3,'P%02d / T%02d'%(panel*12+j+1,s['source_task']),11)
            col='#27804d' if b>a else '#a84455' if b<a else '#b7bec3'
            ln(c,[(a,y),(b,y)],col,2.4)
            c.setFillColor(HexColor(colors[0]));c.circle(a,y,4,fill=1,stroke=0)
            c.setFillColor(HexColor(colors[1]));c.rect(b-3,y-3,6,6,fill=1,stroke=0)
            if a==b:
                c.setStrokeColor(HexColor(colors[0]));c.setLineWidth(1.2);c.circle(a,y,5,fill=0,stroke=1)
    txt(c,28,14,'Circle: BC   Square: DPPO u32   Green link: gain   Red link: loss   T: source task',10)
    save(c,name)
    name='figure_05_same_state_continuations'
    c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=(720,535))
    txt(c,28,511,'Executed continuation after a shared observation history',15)
    txt(c,28,491,'All five paired draws; dashed blue: BC; solid orange: DPPO u32',11)
    chosen=[1,4,13,12]  # P02, P05, P14: recovery examples; P13: ground-group loss.
    details=[]
    for n,index in enumerate(chosen):
        state=states[index];f=lookup[state['state_id']];goal=np.array(f['header']['task']['goal_pos'])
        series=[]
        for pi,policy in enumerate(['bc','rl_2f3f9914db78_u32']):
            path=run/'recovery'/policy/(state['state_id']+'.json')
            hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
            result=json.loads(path.read_text(encoding='utf-8'))
            assert result['actual_use_base_policy']==(pi==0)
            for flight in result['continuations']:
                times=[0.];dist=[flight['initial_distance']];elapsed=0.
                for row in flight['rows']:
                    points=np.array(row['executed_path']);dur=row['executed_time_s']
                    for k,point in enumerate(points[1:],1):
                        times.append(elapsed+min(k*.3,dur));dist.append(float(np.linalg.norm(point-goal)))
                    elapsed+=dur
                assert abs(dist[-1]-flight['final_distance'])<1e-5
                assert elapsed<=(60-f['decision'])*1.2+1e-6
                series.append((pi,flight['draw'],times,dist,flight['outcome']))
        x=55+(n%2)*355;y=284-(n//2)*225;w=285;h=155
        xmax=(60-f['decision'])*1.2;ymax=math.ceil(max(max(s[3]) for s in series)/2)*2
        def pos(t,d):return (x+t/xmax*w,y+d/ymax*h)
        for v in [0,ymax/2,ymax]:
            ln(c,[pos(0,v),pos(xmax,v)],'#e1e5e8',.6);txt(c,x-28,pos(0,v)[1]-3,'%g'%v,9)
        for t in [0,xmax/2,xmax]:txt(c,pos(t,0)[0]-8,y-15,'%.1f'%t,9)
        ln(c,[pos(0,.5),pos(xmax,.5)],'#858585',.7,True)
        for pi,draw,ts,ds,outcome in series:
            ln(c,[pos(t,d) for t,d in zip(ts,ds)],colors[pi],.85,pi==0)
            xx,yy=pos(ts[-1],ds[-1]);c.setStrokeColor(HexColor(colors[pi]));c.setFillColor(HexColor(colors[pi]))
            if outcome=='reached':c.circle(xx,yy,2.4,fill=1,stroke=0)
            elif outcome=='collision':
                ln(c,[(xx-3,yy-3),(xx+3,yy+3)],colors[pi]);ln(c,[(xx-3,yy+3),(xx+3,yy-3)],colors[pi])
            else:c.rect(xx-2.5,yy-2.5,5,5,fill=0,stroke=1)
        txt(c,x,y+h+13,'P%02d / T%02d: BC %d/5, u32 %d/5'%(index+1,state['source_task'],state['bc_reached'],state['rl_reached']),11)
        txt(c,x+42,y-32,'Time since shared state (s)',10)
        txt(c,x+5,y+h-12,'Goal distance (m)',9)
        details.append(dict(state_id=state['state_id'],p=index+1,task=state['source_task'],original_decision=f['decision'],curves=len(series)))
    txt(c,28,12,'Goal distance (m); dashed level: 0.5 m. End: filled circle arrival; cross collision; open square timeout.',9)
    save(c,name)
    lines=['# P3完整数据附表','','编号P为冻结状态顺序；N为新任务顺序；T为旧开发任务编号。均不是训练seed。','',
           '## 共同初态全部24状态','','| P | 状态ID | T | 来源策略 | 原decision | 分组 | BC到达/5 | u32到达/5 | 新增 | 流失 |','|---:|---|---:|---|---:|---|---:|---:|---:|---:|']
    for i,s in enumerate(states):
        lines.append('| %d | %s | %d | %s | %d | %s | %d | %d | %d | %d |'%(i+1,s['state_id'],s['source_task'],s['source_policy'],s['decision'],s['group'],s['bc_reached'],s['rl_reached'],s['rescue'],s['lost']))
    lines+=['','## 新任务全部24项','','结局顺序为到达/碰撞/超时，各策略每任务合计5。','',
            '| N | task_id | 世界 | 直连受阻 | 已见几何 | BC结局 | u32结局 |','|---:|---|---|---|---|---|---|']
    for t in data['per_task']:
        vals=['/'.join(str(t['outcomes'][p].get(k,0)) for k in ['reached','collision','time_limit']) for p in ['bc','rl_2f3f9914db78_u32']]
        lines.append('| %d | %s | %s | %s | %s | %s | %s |'%(t['task'],t['task_id'],t['world_id'],t['blocked'],t['seen_geometry'],*vals))
    (OUT/'P3_data_tables.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (OUT/'P3_figure_sources.json').write_text(json.dumps(dict(source_hashes=hashes,continuation_panels=details,
        all_states=24,all_new_tasks=24,selection='Three improved pre-deviation/stall examples plus one same-group loss; all states reported in figure 4'),indent=2)+'\n',encoding='utf-8')
    print('P3: verified 24 states, 24 new tasks and 40 raw continuation curves; figures 4/5 and tables generated.')


if '--p3-only' in sys.argv:
    paper_p3()
    raise SystemExit(0)

SOURCE = ROOT / 'jindu/2026-10-15_v3_全策略原轨迹分析数据.json'
SHA = '017dc1690eee251e646fdc7f5a68f7e4f16f6a5200d4815d0dab37950d1d69fa'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SHA
DATA = json.loads(SOURCE.read_text(encoding='utf-8'))
POLICIES = ['bc', 'rl_2f3f9914db78_u32']
RECORDS = [r for r in DATA['records'] if r['policy'] in POLICIES]
INDEX = {(r['policy'], r['task'], r['repeat']): r for r in RECORDS}
assert len(RECORDS) == len(INDEX) == 840
TASKS = sorted({r['task'] for r in RECORDS})
assert len(TASKS) == 84
BLUE, RED, GRAY = '#23688d', '#b64d35', '#737e85'
REPEAT_COLORS = ['#2166ac', '#d6604d', '#36844b', '#8b5ca5', '#c18400']


def paired(predicate):
    a = [r for r in RECORDS if r['policy'] == 'bc' and predicate(r)]
    b = [INDEX[(POLICIES[1], r['task'], r['repeat'])] for r in a]
    return dict(n=len(a), bc=dict(Counter(r['outcome'] for r in a)),
                rl=dict(Counter(r['outcome'] for r in b)),
                both=sum(x['success'] and y['success'] for x, y in zip(a, b)),
                new=sum(not x['success'] and y['success'] for x, y in zip(a, b)),
                lost=sum(x['success'] and not y['success'] for x, y in zip(a, b)))


stats = {'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': SHA,
         'all': paired(lambda r: True), 'blocked': paired(lambda r: r['blocked']),
         'unblocked': paired(lambda r: not r['blocked']),
         'dense_blocked': paired(lambda r: r['blocked'] and r['family'] in
                                ['bottleneck_corridor','cul_de_sac_trap','s_turn_multi_obstacle'])}
task_rows = []
for t in TASKS:
    a = INDEX[('bc', t, 1)]
    counts = [sum(INDEX[(p, t, k)]['success'] for k in range(1, 6)) for p in POLICIES]
    task_rows.append(dict(task=t, blocked=a['blocked'], family=a['family'],
                          world=a['world'], bc=counts[0], rl=counts[1], delta=counts[1]-counts[0],
                          new=paired(lambda r: r['task']==t)['new'],
                          lost=paired(lambda r: r['task']==t)['lost']))
stats['tasks'] = task_rows
stats['zero_net_exchange']=[r for r in task_rows if r['delta']==0 and r['new']>0]
stats['task_change'] = dict(Counter('up' if r['delta'] > 0 else 'down' if r['delta'] < 0 else 'equal' for r in task_rows))
stats['families'] = {f: paired(lambda r: r['family'] == f) for f in sorted({r['family'] for r in RECORDS})}
common = [(r, INDEX[(POLICIES[1], r['task'], r['repeat'])]) for r in RECORDS
          if r['policy'] == 'bc' and r['success'] and INDEX[(POLICIES[1], r['task'], r['repeat'])]['success']]
stats['common_success'] = {'n': len(common)}
for key in ['path_length_m', 'duration', 'max_cross_track_m', 'z_span_m']:
    stats['common_success'][key] = [dict(mean=float(np.mean([pair[i][key] for pair in common])),
                                       median=float(np.median([pair[i][key] for pair in common]))) for i in range(2)]

# Paired endpoint changes are not inferable from marginal totals.
labels=['reached','collision','time_limit']
matrix=np.zeros((3,3),dtype=int)
for r in RECORDS:
    if r['policy']=='bc':
        q=INDEX[(POLICIES[1],r['task'],r['repeat'])]
        matrix[labels.index(r['outcome']),labels.index(q['outcome'])]+=1
assert matrix.sum()==420
stats['paired_terminal_matrix']={'rows_bc':labels,'columns_rl':labels,'counts':matrix.tolist()}
stats['common_success_paired_differences']={}
for key in ['path_length_m','duration']:
    differences=np.array([b[key]-a[key] for a,b in common])
    q1,median,q3=np.quantile(differences,[.25,.5,.75])
    stats['common_success_paired_differences'][key]={
        'direction':'RL minus BC','quantile_method':'linear',
        'mean':float(differences.mean()),'median':float(median),
        'q1':float(q1),'q3':float(q3),'iqr':float(q3-q1),
        'positive':int((differences>0).sum()),'negative':int((differences<0).sum()),
        'zero':int((differences==0).sum())}

traces = {}
case_rows = []
PHASE_SOURCE=ROOT/'jindu/2026-10-17_v3_轨迹行为分段与观测审计完整数据.json'
phase_data=json.loads(PHASE_SOURCE.read_text(encoding='utf-8'))
phase_index={(r['policy'],r['task'],r['repeat']):r for r in phase_data['records']}
stats['phase_source']={'path':str(PHASE_SOURCE.relative_to(ROOT)),
                       'sha256':hashlib.sha256(PHASE_SOURCE.read_bytes()).hexdigest()}
for t in [17,20,30,32,47,75]:
    for p in POLICIES:
        for k in range(1, 6):
            r = INDEX[(p, t, k)]
            raw = ROOT / r['source']
            rows = [json.loads(s) for s in raw.read_text(encoding='utf-8').splitlines()]
            start, end = rows[0], rows[-1]
            steps = [s for s in rows if s['type'] == 'transition']
            assert start['use_base_policy'] == (p == 'bc')
            assert end['safe_arrival'] == r['success']
            paths = [np.asarray(s['executed_path'], dtype=float) for s in steps]
            for a, b in zip(paths, paths[1:]):
                assert np.allclose(a[-1], b[0], atol=1e-6)
            xyz = np.vstack([paths[0][:1]] + [a[1:] for a in paths])
            goal = np.asarray(start['task']['goal_pos'])
            length = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
            duration = sum(s['executed_time_s'] for s in steps)
            assert abs(length-r['path_length_m']) < 1e-5
            assert abs(duration-r['duration']) < 1e-5
            assert abs(np.linalg.norm(xyz[-1]-goal)-r['final_goal_distance_m']) < 1e-5
            delta=np.diff(xyz,axis=0)
            projection=np.clip(np.sum((goal-xyz[:-1])*delta,axis=1)/
                               np.maximum(np.sum(delta*delta,axis=1),1e-30),0,1)
            closest=float(np.linalg.norm(xyz[:-1]+projection[:,None]*delta-goal,axis=1).min())
            assert abs(closest-r['min_goal_distance_m']) < 1e-5
            # Distance panel uses decision endpoints, with actual elapsed time.
            times = np.r_[0., np.cumsum([s['executed_time_s'] for s in steps])]
            endpoints = np.vstack([paths[0][0]] + [a[-1] for a in paths])
            distances = np.linalg.norm(endpoints-goal, axis=1)
            phase=phase_index[(p,t,k)]
            assert phase['source']==r['source'] and phase['outcome']==r['outcome']
            passed=phase['first_passed_initial_blockers']
            if passed is not None:
                assert abs(distances[passed]-phase['distance_after_passing']) < 1e-5
            vertex_time=np.concatenate([np.array([0.])]+[
                times[i]+np.minimum(np.arange(1,len(path))*.3,s['executed_time_s'])
                for i,(path,s) in enumerate(zip(paths,steps))])
            assert len(vertex_time)==len(xyz) and abs(vertex_time[-1]-duration)<1e-6
            ci=int(np.argmin(np.linalg.norm(xyz[:-1]+projection[:,None]*delta-goal,axis=1)))
            closest_time=float(vertex_time[ci]+projection[ci]*(vertex_time[ci+1]-vertex_time[ci]))
            traces[(p, t, k)] = dict(start=start, xyz=xyz, time=times, distance=distances,
                                      vertex_time=vertex_time,closest_time=closest_time,
                                      endpoints=endpoints,passed=passed,steps=steps)
            case_rows.append({**{key: r[key] for key in ['task','repeat','policy','outcome','path_length_m','duration','min_goal_distance_m','final_goal_distance_m']},
                              'max_endpoint_goal_distance_m': float(distances.max()),
                              'continuous_min_time_s':closest_time,
                              'first_passed_initial_blockers':passed,
                              'distance_after_passing':phase['distance_after_passing'],
                              'final_clear_run':phase['final_clear_run'],
                              'raw_source': r['source'], 'raw_sha256': hashlib.sha256(raw.read_bytes()).hexdigest()})
stats['cases'] = case_rows
stats['post_passage_description']=[]
for t in [20,47]:
    for k in range(1,6):
        tr=traces[(POLICIES[1],t,k)]
        # Descriptive extrema of decision endpoints, not recovery thresholds.
        ds=tr['distance']; turns=np.flatnonzero((ds[1:-1]<ds[:-2]) & (ds[1:-1]<=ds[2:]))+1
        start_index=tr['passed'] if tr['passed'] is not None else 0
        turns=turns[turns>=start_index]
        valleys=[]
        for j in turns:
            peak=j+int(np.argmax(ds[j:]))
            valleys.append(dict(time=float(tr['time'][j]),distance=float(ds[j]),
                                later_max_time=float(tr['time'][peak]),later_max_distance=float(ds[peak])))
        stats['post_passage_description'].append(dict(task=t,repeat=k,extrema=valleys))
# Exact line/rotated-box XY overlap intervals, used only to explain projections.
stats['task75_box_projection']=[]
for k in range(1,6):
    tr=traces[('bc',75,k)]
    for ob in tr['start']['geometry']:
        if ob['shape']!='box': continue
        ca,sa=math.cos(ob['yaw']),math.sin(ob['yaw'])
        rot=np.array([[ca,sa],[-sa,ca]])
        xy=(tr['xyz'][:,:2]-[ob['x'],ob['y']])@rot.T
        intervals=[]
        for i,(a,b) in enumerate(zip(xy[:-1],xy[1:])):
            lo,hi=0.,1.
            for j,half in enumerate([ob['size_x']/2,ob['size_y']/2]):
                dv=b[j]-a[j]
                if abs(dv)<1e-12:
                    if abs(a[j])>half: hi=-1.;break
                else:
                    v=sorted([(-half-a[j])/dv,(half-a[j])/dv]);lo=max(lo,v[0]);hi=min(hi,v[1])
            if lo<=hi:
                z=tr['xyz'][i,2]+np.array([lo,hi])*(tr['xyz'][i+1,2]-tr['xyz'][i,2])
                ts=tr['vertex_time'][i]+np.array([lo,hi])*(tr['vertex_time'][i+1]-tr['vertex_time'][i])
                intervals.append((float(z.min()),float(z.max()),float(ts[0]),float(ts[1])))
        if intervals:
            zmin=min(v[0] for v in intervals); zmax=max(v[1] for v in intervals)
            bottom=ob['z']-ob['size_z']/2;top=ob['z']+ob['size_z']/2
            stats['task75_box_projection'].append(dict(repeat=k,obstacle=ob['name'],
                z_min=zmin,z_max=zmax,bottom=bottom,top=top,
                start_s=min(v[2] for v in intervals),end_s=max(v[3] for v in intervals),
                above_clearance=zmin-.1-top,below_clearance=bottom-zmax-.1))
tr=traces[(POLICIES[1],17,2)];bc17=traces[('bc',17,2)]
endpos=tr['xyz'][-1];event_time=float(tr['time'][-1])
candidates=[o for o in tr['start']['geometry'] if o['shape']=='cylinder'
            and o['z']-o['height']/2-.1 <= endpos[2] <= o['z']+o['height']/2+.1]
ob=min(candidates,key=lambda o:abs(np.linalg.norm(endpos[:2]-[o['x'],o['y']])-o['radius']-.1))
bcpos=np.array([np.interp(event_time,bc17['vertex_time'],bc17['xyz'][:,j]) for j in range(3)])
stats['task17_paired_collision']=dict(repeat=2,time_s=event_time,
    zero_based_decision=tr['steps'][-1]['decision'],event_segment=tr['steps'][-1]['event_segment'],
    rl_position=endpos.tolist(),bc_position_at_same_time=bcpos.tolist(),obstacle=ob['name'],
    rl_radial_surface_gap=float(np.linalg.norm(endpos[:2]-[ob['x'],ob['y']])-ob['radius']),
    bc_radial_surface_gap=float(np.linalg.norm(bcpos[:2]-[ob['x'],ob['y']])-ob['radius']))
(OUT/'P2_results.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')


def text(c, x, y, s, size=10, color='#263746', align='left'):
    c.setFillColor(HexColor(color)); c.setFont('Helvetica', size)
    getattr(c, {'left':'drawString','center':'drawCentredString','right':'drawRightString'}[align])(x,y,str(s))


def line(c, points, color, width=1, dashed=False):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width)
    c.setDash(3,2) if dashed else c.setDash()
    p=c.beginPath(); p.moveTo(*points[0])
    for xy in points[1:]: p.lineTo(*xy)
    c.drawPath(p); c.setDash()


def finish(c, name):
    c.save()
    pdf=pdfium.PdfDocument(str(OUT/(name+'.pdf')))
    pdf[0].render(scale=2).to_pil().save(OUT/(name+'.png'))
    pdf.close()


def figure2():
    name='figure_02_paired_results'
    c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=(720,490))
    text(c,35,465,'(a) Safe-arrival exchange: 420 paired evaluations',14)
    text(c,360,439,'Net change = +9  (68 gained - 59 lost)',14,align='center')
    s=stats['all']
    groups=[('Both succeed',s['both'],'#b4bbc0'),('Gained (RL only)',s['new'],'#277c55'),('Lost (BC only)',s['lost'],'#ab4653'),
            ('Both fail',s['n']-s['both']-s['new']-s['lost'],'#b4bbc0')]
    for i,(label,n,col) in enumerate(groups):
        x=55+i*170; h=n/240*100
        c.setFillColor(HexColor(col)); c.rect(x,310,95,h,fill=1,stroke=0)
        text(c,x+47.5,317+h,n,12,align='center'); text(c,x+47.5,293,label,11,align='center')
    text(c,35,261,'(b) Net arrival change per task: RL - BC (five repeats)',14)
    x0,y0,w,h=45,105,640,100
    ordered=sorted(task_rows,key=lambda r:(not r['blocked'],-r['delta'],r['task']))
    nb=sum(r['blocked'] for r in ordered)
    split=x0+nb*w/84
    text(c,(x0+split)/2,229,f'Blocked ({nb} tasks)',12,RED,align='center')
    text(c,(split+x0+w)/2,229,f'Unblocked ({84-nb} tasks)',12,BLUE,align='center')
    line(c,[(split,94),(split,218)],GRAY,.6,True)
    for v in [-5,0,5]:
        y=y0+(v+5)/10*h
        line(c,[(x0,y),(x0+w,y)],'#d7dde0',.5)
        text(c,x0-10,y-3,v,10,align='right')
    for i,row in enumerate(ordered):
        t,v=row['task'],row['delta']; x=x0+(i+.5)*w/84
        col=RED if row['blocked'] else BLUE
        c.setFillColor(HexColor(col))
        if v: c.rect(x-2.5,y0+h/2 if v>=0 else y0+(v+5)/10*h,5,abs(v)*h/10,fill=1,stroke=0)
        else: c.circle(x,y0+h/2,1.6,fill=1,stroke=0)
        if t in [20,30,32,17,47,75]:
            text(c,x,y0+(v+5)/10*h+(6 if v>=0 else (-14 if t!=47 else -26)),t,10,align='center')
    text(c,360,76,'Grouped by initial direct-path obstruction; sorted by change, then task ID.',10,align='center')
    text(c,360,59,'Labels identify blocked tasks with changes. Dots retain all zero-net tasks.',10,align='center')
    d=stats['task_change']
    text(c,360,40,f"{d['up']} improved / {d['down']} declined / {d['equal']} zero net; no gain-loss cancellation in zero-net tasks.",10,align='center')
    text(c,360,22,'Binary outcomes isolate arrival exchange; collision / timeout transitions are in Table S2.4.',10,align='center')
    finish(c,name)


def marker(c,x,y,outcome,color,size=3):
    c.setStrokeColor(HexColor(color));c.setLineWidth(1.3);c.setDash()
    if outcome=='reached':c.circle(x,y,size,stroke=1,fill=0)
    elif outcome=='collision':c.line(x-size,y-size,x+size,y+size);c.line(x-size,y+size,x+size,y-size)
    elif outcome=='time_limit':line(c,[(x,y+size),(x-size,y-size),(x+size,y-size),(x,y+size)],color,1.3)
    elif outcome=='passed':line(c,[(x,y+size),(x-size,y),(x,y-size),(x+size,y),(x,y+size)],color,1)
    else:raise ValueError(outcome)


def map_panel(c, t, p, x, y, w, h, limits):
    xmin,xmax,ymin,ymax=limits
    scale=min(w/(xmax-xmin),h/(ymax-ymin))
    left=x+(w-(xmax-xmin)*scale)/2; bottom=y+(h-(ymax-ymin)*scale)/2
    def xy(a,b): return left+(a-xmin)*scale,bottom+(b-ymin)*scale
    c.saveState()
    clip=c.beginPath();clip.rect(left,bottom,(xmax-xmin)*scale,(ymax-ymin)*scale);c.clipPath(clip,stroke=0)
    first=traces[(p,t,1)]['start']
    for ob in first['geometry']:
        a,b=xy(ob['x'],ob['y']); c.setFillColor(HexColor('#e1e4e6')); c.setStrokeColor(HexColor('#aeb6bc')); c.setLineWidth(.5)
        if ob['shape']=='cylinder': c.circle(a,b,ob['radius']*scale,fill=1,stroke=1)
        elif ob['shape']=='box':
            c.saveState();c.translate(a,b);c.rotate(ob['yaw']*180/math.pi)
            c.rect(-ob['size_x']*scale/2,-ob['size_y']*scale/2,ob['size_x']*scale,ob['size_y']*scale,fill=1,stroke=1);c.restoreState()
        else: raise ValueError(ob['shape'])
    for k in range(1,6):
        tr=traces[(p,t,k)]; pts=[xy(a,b) for a,b in tr['xyz'][:,:2]]
        line(c,pts,REPEAT_COLORS[k-1],1.2)
        marker(c,*pts[-1],INDEX[(p,t,k)]['outcome'],REPEAT_COLORS[k-1])
        if tr['passed'] is not None:
            marker(c,*xy(*tr['endpoints'][tr['passed'],:2]),'passed',REPEAT_COLORS[k-1])
    a,b=xy(*first['task']['start_pos'][:2]);c.setFillColor(HexColor('#222222'));c.rect(a-3,b-3,6,6,fill=1,stroke=0)
    a,b=xy(*first['task']['goal_pos'][:2]);c.setStrokeColor(HexColor('#111111'));c.setLineWidth(1.2);c.circle(a,b,.5*scale,fill=0,stroke=1)
    text(c,a+5,b+5,'G',9)
    c.restoreState()
    line(c,[xy(xmin,ymax),xy(xmin,ymin),xy(xmax,ymin)],'#444444',.7)
    for v in range(math.ceil(xmin/5)*5,math.floor(xmax/5)*5+1,5):
        a,b=xy(v,ymin);text(c,a,b-12,v,10,align='center')
    for v in range(math.ceil(ymin/5)*5,math.floor(ymax/5)*5+1,5):
        a,b=xy(xmin,v);text(c,a-5,b-3,v,10,align='right')
    text(c,x+w/2,y-25,'x (m)',10,align='center');text(c,left-22,y+h/2,'y',10)
    n=sum(INDEX[(p,t,k)]['success'] for k in range(1,6))
    text(c,x+w/2,y+h+10,('BC' if p=='bc' else 'DPPO u32')+f': {n}/5 safe arrivals',11,align='center')


def distance_panel(c,t,x,y,w,h,zoom=False):
    xmin,xmax=(50,72) if zoom else (0,72)
    ymin,ymax=(.45,1.6) if zoom else (0,math.ceil(max(traces[(p,t,k)]['distance'].max() for p in POLICIES for k in range(1,6))/5)*5)
    def dp(a,b):return x+(a-xmin)/(xmax-xmin)*w,y+(b-ymin)/(ymax-ymin)*h
    for v in ([.5,1,1.5] if zoom else range(0,ymax+1,5)):
        line(c,[dp(xmin,v),dp(xmax,v)],'#e0e3e5',.5);text(c,x-5,dp(xmin,v)[1]-3,v,10,align='right')
    c.saveState();clip=c.beginPath();clip.rect(x-4,y-4,w+8,h+8);c.clipPath(clip,stroke=0)
    for p in ([POLICIES[1]] if zoom else POLICIES):
        for k in range(1,6):
            tr=traces[(p,t,k)]
            ts=tr['vertex_time'] if zoom else tr['time']
            ds=np.linalg.norm(tr['xyz']-tr['start']['task']['goal_pos'],axis=1) if zoom else tr['distance']
            line(c,[dp(a,b) for a,b in zip(ts,ds)],REPEAT_COLORS[k-1],1.2,p=='bc')
            marker(c,*dp(ts[-1],ds[-1]),INDEX[(p,t,k)]['outcome'],REPEAT_COLORS[k-1])
            if not zoom and tr['passed'] is not None:
                j=tr['passed'];marker(c,*dp(ts[j],ds[j]),'passed',REPEAT_COLORS[k-1])
    line(c,[dp(xmin,.5),dp(xmax,.5)],'#555555',.8,True)
    if t==20 and not zoom:
        line(c,[dp(24,0),dp(24,ymax)],GRAY,.7,True)
        text(c,*dp(25,ymax-2),'24 s: passage',10)
    if zoom:
        tr=traces[(POLICIES[1],30,3)];r=INDEX[(POLICIES[1],30,3)]
        px,py=dp(tr['closest_time'],r['min_goal_distance_m'])
        c.setFillColor(HexColor(REPEAT_COLORS[2]));c.circle(px,py,2.4,fill=1,stroke=0)
        text(c,x+6,y+h-15,'R3 minimum = 0.514 m',10,REPEAT_COLORS[2])
        text(c,x+6,y+h-29,'Arrival threshold = 0.500 m',10)
    c.restoreState()
    for v in ([50,60,70,72] if zoom else [0,24,48,72]):text(c,dp(v,ymin)[0],y-15,v,10,align='center')
    text(c,x+w/2,y-31,'Time (s)',11,align='center')
    text(c,x+w/2,y+h+12,('Task 30: near-goal detail' if zoom else f'Task {t}: distance to goal (m)'),11,align='center')


def height_panels(c):
    """T32: body bottom and one common low obstacle, all five RL repeats.

    Bold intervals are exact line/circle intersections in XY, not sampled
    occupancy or an assumed collision. The obstacle is crossed by all five.
    """
    ob=next(o for o in traces[(POLICIES[1],32,1)]['start']['geometry'] if o['name']=='trap_scatter_12')
    assert ob['shape']=='cylinder'
    top=ob['z']+ob['height']/2
    text(c,360,186,'T32: existing vertical clearance (all five RL repeats)',12,align='center')
    for k in range(1,6):
        tr=traces[(POLICIES[1],32,k)];ts=tr['vertex_time'];xyz=tr['xyz']
        x=32+(k-1)*142;y=53;w=112;h=104
        def zpos(t,z):return x+t/72*w,y+(z-2.4)/1.8*h
        for z in [2.5,3.0,3.5,4.0]:
            line(c,[zpos(0,z),zpos(72,z)],'#e0e3e5',.5)
            if k==1:text(c,x-4,zpos(0,z)[1]-3,z,9,align='right')
        line(c,[zpos(0,top),zpos(72,top)],'#666666',.8,True)
        line(c,[zpos(t,z-.1) for t,z in zip(ts,xyz[:,2])],REPEAT_COLORS[k-1],.8)
        n=0
        for i,(a,b) in enumerate(zip(xyz[:-1],xyz[1:])):
            v=b[:2]-a[:2];q=a[:2]-[ob['x'],ob['y']]
            aa=float(v@v);bb=2*float(q@v);cc=float(q@q)-ob['radius']**2
            if aa<1e-14: interval=(0,1) if cc<=0 else None
            else:
                disc=bb*bb-4*aa*cc
                if disc<0:continue
                lo=max(0.,(-bb-math.sqrt(disc))/(2*aa));hi=min(1.,(-bb+math.sqrt(disc))/(2*aa))
                interval=(lo,hi) if lo<=hi else None
            if interval is not None:
                n+=1
                pts=[zpos(ts[i]+u*(ts[i+1]-ts[i]),a[2]+u*(b[2]-a[2])-.1) for u in interval]
                line(c,pts,REPEAT_COLORS[k-1],3)
        assert n>0
        marker(c,*zpos(ts[-1],xyz[-1,2]-.1),INDEX[(POLICIES[1],32,k)]['outcome'],REPEAT_COLORS[k-1])
        for t in [0,36,72]:text(c,zpos(t,2.4)[0],y-13,t,9,align='center')
        text(c,x+w/2,166,'R%d / %s'%(k,'arrival' if INDEX[(POLICIES[1],32,k)]['success'] else 'collision'),10,align='center')
    text(c,360,25,'Time (s); vertical axis: body-bottom height (m). Dashed: obstacle top = %.3f m.'%top,10,align='center')
    text(c,360,9,'Bold: exact XY overlap with trap_scatter_12. Positive clearance uses the initial altitude; no climb.',10,align='center')


def figure3(tasks,name):
    main=len(tasks)==3
    cell=240 if main else 360
    width=cell*len(tasks);c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=(width,990 if main else 780))
    if main:
        c.saveState();c.translate(0,210)
    for col,t in enumerate(tasks):
        x=col*cell+37;w=cell-60
        allxyz=np.vstack([traces[(p,t,k)]['xyz'] for p in POLICIES for k in range(1,6)]+[np.asarray(traces[('bc',t,1)]['start']['task']['goal_pos'])[None]])
        bounds=[allxyz[:,:2]]
        for ob in traces[('bc',t,1)]['start']['geometry']:
            # Include complete obstacle footprints, including rotated boxes.
            radius=ob['radius'] if ob['shape']=='cylinder' else math.hypot(ob['size_x'],ob['size_y'])/2
            bounds.append(np.array([[ob['x']-radius,ob['y']-radius],[ob['x']+radius,ob['y']+radius]]))
        bounds=np.vstack(bounds)
        lo=bounds.min(0)-2;hi=bounds.max(0)+2
        limits=(lo[0],hi[0],lo[1],hi[1])
        text(c,x+w/2,756,f'Task {t}',16,align='center')
        for i,p in enumerate(POLICIES): map_panel(c,t,p,x,520-i*235,w,190,limits)
        distance_panel(c,30 if main and t==32 else t,x,100,w,135,zoom=main and t==32)
    for k,col in enumerate(REPEAT_COLORS):text(c,25+k*width/6,35,f'Repeat {k+1}',10,col)
    if len(tasks)==1:
        text(c,width/2,20,'Circle: arrival; cross: collision; triangle: timeout.',8,align='center')
        text(c,width/2,8,'Diamond: passed blockers. Dashed BC / solid RL. See S2.3.',8,align='center')
    else:
        text(c,width/2,19,'Square: start; G: goal; circle: arrival; cross: collision; triangle: timeout; diamond: geometric passage.',10,align='center')
        text(c,width/2,6,'Distance: dashed BC / solid RL. Maps are XY projections, not 3D collision checks.',10,align='center')
    if main:
        c.restoreState();height_panels(c)
    finish(c,name)


def figure_s1():
    name='figure_S1_loss_case'
    c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=(720,650))
    text(c,360,625,'Task 75: lost arrivals under a known observation limitation',15,align='center')
    limits=(-6,15,-16,10)
    for i,p in enumerate(POLICIES):map_panel(c,75,p,45+360*i,310,270,260,limits)
    distance_panel(c,75,45,85,270,160)
    x,y,w,h=415,85,270,160
    def zp(t,z):return x+(t-6)/6*w,y+(z-2.9)/.9*h
    text(c,x+w/2,y+h+12,'BC crosses above the upper wall',11,align='center')
    for z in [3.,3.4,3.8]:
        line(c,[zp(6,z),zp(12,z)],'#e0e3e5',.5);text(c,x-5,zp(6,z)[1]-3,z,10,align='right')
    line(c,[zp(6,3),zp(12,3)],GRAY,1,True)
    text(c,x+5,zp(6,3)[1]+7,'Wall top = 3.0 m',10)
    c.saveState();clip=c.beginPath();clip.rect(x,y,w,h);c.clipPath(clip,stroke=0)
    for k in range(1,6):
        tr=traces[('bc',75,k)];ts=tr['vertex_time'];bottom=tr['xyz'][:,2]-.1
        line(c,[zp(a,b) for a,b in zip(ts,bottom)],REPEAT_COLORS[k-1],.8)
        r=next(r for r in stats['task75_box_projection'] if r['repeat']==k)
        tx=np.r_[r['start_s'],ts[(ts>r['start_s'])&(ts<r['end_s'])],r['end_s']]
        line(c,[zp(a,b) for a,b in zip(tx,np.interp(tx,ts,bottom))],REPEAT_COLORS[k-1],2.5)
    c.restoreState()
    for v in [6,8,10,12]:text(c,zp(v,3)[0],y-15,v,10,align='center')
    text(c,x+w/2,y-31,'Time (s); flight-body bottom height (m)',10,align='center')
    text(c,x+5,y+h-16,'Bold: XY overlaps the wall footprint',10)
    text(c,x+5,y+h-31,'Minimum vertical separation: 0.444 m',10)
    for k,col in enumerate(REPEAT_COLORS):text(c,25+k*120,32,f'Repeat {k+1}',10,col)
    text(c,360,16,'Circle: arrival; cross: collision; diamond: passage. Distance: dashed BC / solid RL.',10,align='center')
    text(c,360,3,'XY overlap is not collision. Known sensor/geometry mismatch remains a confound (S2.3).',10,align='center')
    finish(c,name)


figure2()
figure3([30,20,32],'figure_03_executed_trajectories')
figure_s1()
figure3([17,47],'figure_S2_other_losses')
extra=canvas.Canvas(str(OUT/'figure_S3_task32_distance.pdf'),pagesize=(360,310))
distance_panel(extra,32,40,90,290,165)
for k,col in enumerate(REPEAT_COLORS):text(extra,15+k*69,41,f'Repeat {k+1}',9,col)
text(extra,180,25,'Circle: arrival; cross: collision; diamond: passage.',9,align='center')
text(extra,180,10,'Dashed BC / solid DPPO u32; all five repeats.',10,align='center')
finish(extra,'figure_S3_task32_distance')

# Automatically generated appendix tables, kept separate from authored prose.
lines=['# P2数据附表（自动生成）','', '来源及哈希见[P2_results.json](P2_results.json)。仅整理已有评价，不包含新策略运行。','',
       '## 全部84任务到达计数','', '| 任务 | 直连受阻 | BC/5 | RL/5 | 差值 | 配对新增 | 配对流失 |','|---|---|---:|---:|---:|---:|---:|']
for r in task_rows: lines.append(f"| {r['task']} | {'是' if r['blocked'] else '否'} | {r['bc']} | {r['rl']} | {r['delta']:+d} | {r['new']} | {r['lost']} |")
lines+=['','## 场景家族全部结果','','| 场景家族 | N | BC到达/碰撞/超时 | RL到达/碰撞/超时 |','|---|---:|---|---|']
for f,s in stats['families'].items():
    vals=['/'.join(str(s[p].get(k,0)) for k in ['reached','collision','time_limit']) for p in ['bc','rl']]
    lines.append(f"| {f} | {s['n']} | {vals[0]} | {vals[1]} |")
lines+=['','## 六个案例全部重复','','距离单位m，时间单位s。最近距离采用既有审计对执行线段的计算；成功依据原始事件标签，不对浮点距离重新阈值分类。','',
        '| 任务 | 策略 | 重复 | 终点 | 路长 | 时长 | 最近目标距离 | 终点目标距离 |','|---|---|---:|---|---:|---:|---:|---:|']
for r in case_rows:
    label='BC' if r['policy']=='bc' else 'DPPO u32'
    lines.append(f"| {r['task']} | {label} | {r['repeat']} | {r['outcome']} | {r['path_length_m']:.3f} | {r['duration']:.3f} | {r['min_goal_distance_m']:.3f} | {r['final_goal_distance_m']:.3f} |")
(OUT/'P2_data_tables.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:stats[k] for k in ['all','blocked','unblocked','task_change','common_success']},ensure_ascii=False,indent=2))
print('Verified 60 raw case paths; generated figures 2, 3, S1, S2, S3 and full descriptive tables.')
