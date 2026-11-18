"""第4章（v13）全部派生数字与图4、图7。只读输入：
  台账/论文实验数据主表.xlsx（用户 11-18 上传，sha256 c7a01ca3…）
  台账/69任务轨迹质量补算.xlsx（用户 11-18 上传，sha256 8c96e4bc…）
运行：python 研究报告/analysis_20261118/ch4_analysis.py   输出到 研究报告/analysis_20261118/out/ 与 图表/v13/
"""
import json, math, os
import pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
M=os.path.join(ROOT,'台账','论文实验数据主表.xlsx'); Q=os.path.join(ROOT,'台账','69任务轨迹质量补算.xlsx')
OUT=os.path.join(ROOT,'研究报告','analysis_20261118','out'); FIG=os.path.join(ROOT,'图表','v13')
os.makedirs(OUT,exist_ok=True); os.makedirs(FIG,exist_ok=True)
R={}
def wilson(k,n,z=1.959964):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return [round(100*(c-h),1),round(100*(c+h),1)]
k=pd.read_excel(M,sheet_name='运动学明细',header=3); g=pd.read_excel(M,sheet_name='Gazebo明细',header=3)
DIFF=['稀疏','适中','密集']
# 表4 / 表7：任务成功与任务失败类型
def table(df,methods):
    rows=[]
    for m in methods:
        s=df[df['方法']==m]; r={'方法':m,'总体':f"{(s['任务结局类型']=='成功').sum()}/{len(s)}"}
        for d in DIFF:
            t=s[s['难度']==d]; r[d]=f"{(t['任务结局类型']=='成功').sum()}/{len(t)}"
        r['碰撞失败']=int((s['任务结局类型']=='碰撞').sum()); r['超时失败']=int((s['任务结局类型']=='超时').sum()); rows.append(r)
    return rows
KM=['UAV-iDP3','Reg-DPPO w/o Stage II','Single-stage DPPO','Reg-DPPO w/o BC reg.','本文方法','EGO-Planner-Swarm','Fast-Planner kino','SUPER']
GM=['UAV-iDP3','本文方法','EGO-Planner','Fast-Planner kino','SUPER']
R['表4']=table(k,KM); R['表7']=table(g,GM)
# 逐次飞行（运动学原始结局）
for m in ['UAV-iDP3','本文方法']:
    s=k[k['方法']==m]; v=pd.concat([s[f'重复{i}原始结局'] for i in range(1,6)]).value_counts()
    R[f'运动学飞行结局_{m}']={a:int(b) for a,b in v.items()}
# 图4：UAV-iDP3 → 本文方法 的任务结局转移
kp=k.pivot_table(index=['任务ID','难度'],columns='方法',values='任务结局类型',aggfunc='first').reset_index()
def xt(a,b,sub=None):
    s=kp if sub is None else kp[kp['难度']==sub]
    return {f'{i}->{j}':int(((s[a]==i)&(s[b]==j)).sum()) for i in ['成功','碰撞','超时'] for j in ['成功','碰撞','超时']}
R['转移_UAV-iDP3_本文方法']={d:xt('UAV-iDP3','本文方法',d) for d in [None]+DIFF}
# 表6：第一阶段 → 第二阶段
ab={}
for m in ['本文方法','Reg-DPPO w/o BC reg.','Single-stage DPPO']:
    t=xt('Reg-DPPO w/o Stage II',m); keep=t['成功->成功']; ref=128
    ab[m]={'保持':keep,'遗忘为碰撞':t['成功->碰撞'],'遗忘为超时':t['成功->超时'],'新增(原碰撞)':t['碰撞->成功'],'新增(原超时)':t['超时->成功'],
           '最终':int((kp[m]=='成功').sum()),'保持率%':round(100*keep/ref,1),'Wilson95':wilson(keep,ref)}
R['表6']=ab
# 表5：69 任务轨迹质量
q=pd.read_excel(Q,sheet_name='五方法汇总'); pdiff=pd.read_excel(Q,sheet_name='配对差值汇总')
R['表5']=q.round(3).to_dict('records'); R['表5_配对']=pdiff.round(4).to_dict('records')
# 图7：两平台共有任务上的逐次飞行成功率（主表标签）
pairs=[('UAV-iDP3','UAV-iDP3'),('本文方法','本文方法'),('EGO-Planner-Swarm','EGO-Planner'),('Fast-Planner kino','Fast-Planner kino'),('SUPER','SUPER')]
common=sorted(set(g['任务ID'])&set(k['任务ID'])); R['共有任务数']=len(common)
f7=[]
for km,gm in pairs:
    ks=k[(k['方法']==km)&(k['任务ID'].isin(common))]; gs=g[(g['方法']==gm)&(g['任务ID'].isin(common))]
    kl=pd.concat([ks[f'重复{i}'] for i in range(1,6)]); gl=pd.concat([gs['重复1'],gs['重复2']])
    kr=pd.concat([ks[f'重复{i}原始结局'] for i in range(1,6)]).value_counts(); gr=pd.concat([gs['重复1原始结局'],gs['重复2原始结局']]).value_counts()
    f7.append({'方法':gm if gm!=km else km,'运动学飞行':f"{(kl=='成功').sum()}/{len(kl)}",'运动学%':round(100*(kl=='成功').mean(),1),
               'Gazebo飞行':f"{(gl=='成功').sum()}/{len(gl)}",'Gazebo%':round(100*(gl=='成功').mean(),1),
               '运动学原始碰撞%':round(100*kr.get('碰撞',0)/len(kl),1),'运动学原始超时%':round(100*kr.get('超时',0)/len(kl),1),
               'Gazebo原始碰撞%':round(100*gr.get('碰撞',0)/len(gl),1),'Gazebo原始超时%':round(100*gr.get('超时',0)/len(gl),1)})
R['图7']=f7
gp=g.pivot_table(index='任务ID',columns='方法',values='任务结局类型',aggfunc='first')
kpi=kp.set_index('任务ID')
R['UAV-iDP3_运动学到Gazebo_共有任务']={f'{i}->{j}':int(((kpi.loc[common,'UAV-iDP3']==i)&(gp.loc[common,'UAV-iDP3']==j)).sum()) for i in ['成功','碰撞','超时'] for j in ['成功','碰撞','超时']}
R['本文方法_运动学到Gazebo_共有任务']={f'{i}->{j}':int(((kpi.loc[common,'本文方法']==i)&(gp.loc[common,'本文方法']==j)).sum()) for i in ['成功','碰撞','超时'] for j in ['成功','碰撞','超时']}
R['Gazebo转移_UAV-iDP3_本文方法']={f'{i}->{j}':int(((gp['UAV-iDP3']==i)&(gp['本文方法']==j)).sum()) for i in ['成功','碰撞','超时'] for j in ['成功','碰撞','超时']}
# 训练曲线（图6）
tc=pd.read_excel(M,sheet_name='训练曲线',header=3)
R['训练曲线_第二阶段']={m:{'KL最大':float(s[s['更新轮数']>128]['近似KL'].max()),'KL最大轮':int(s.loc[s[s['更新轮数']>128]['近似KL'].idxmax(),'更新轮数']),
   '采集成功率范围':[float(s[s['更新轮数']>128]['训练采集成功率_百分数'].min()),float(s[s['更新轮数']>128]['训练采集成功率_百分数'].max())],'第128轮KL':float(s[s['更新轮数']==128]['近似KL'].iloc[0])} for m,s in tc.groupby('方法')}
json.dump(R,open(os.path.join(OUT,'ch4_numbers.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1,default=str)

# ---------- 图件 ----------
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#52514e','axes.labelcolor':'#0b0b0b','xtick.color':'#52514e','ytick.color':'#52514e'})
COL={'成功':'#2a78d6','碰撞':'#eb6834','超时':'#6250d6'}; EN={'成功':'Success','碰撞':'Collision','超时':'Timeout'}
# 图4：三类难度，每类三根横条（UAV-iDP3 的任务结局），条内按本文方法结局分段
fig,axes=plt.subplots(1,3,figsize=(7.2,2.3),sharex=True,sharey=True)
for ax,d,lab in zip(axes,DIFF,['(a) Sparse','(b) Moderate','(c) Dense']):
    t=R['转移_UAV-iDP3_本文方法'][d]
    for yi,src in enumerate(['成功','碰撞','超时']):
        left=0
        for dst in ['成功','碰撞','超时']:
            v=t[f'{src}->{dst}']
            if v==0: continue
            ax.barh(2-yi,v,left=left,height=0.62,color=COL[dst],edgecolor='#fcfcfb',linewidth=1.5)
            if v>=3: ax.text(left+v/2,2-yi,str(v),ha='center',va='center',color='white',fontsize=8,fontweight='bold')
            left+=v
        tot=sum(t[f'{src}->{x}'] for x in ['成功','碰撞','超时'])
        ax.text(left+0.8,2-yi,f'n={tot}',va='center',fontsize=7.5,color='#52514e')
    ax.set_yticks([2,1,0]); ax.set_yticklabels(['Success','Collision','Timeout'])
    ax.set_title(lab,fontsize=9,loc='left'); ax.set_xlim(0,46); ax.grid(axis='x',color='#e6e5e0',linewidth=0.6); ax.set_axisbelow(True)
axes[0].set_ylabel('UAV-iDP3 task outcome'); axes[1].set_xlabel('Number of tasks')
h=[plt.Rectangle((0,0),1,1,color=COL[x]) for x in ['成功','碰撞']]
fig.legend(h,['Proposed: success','Proposed: collision'],loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(0.5,-0.02),fontsize=8)
fig.tight_layout(rect=(0,0.08,1,1)); fig.savefig(os.path.join(FIG,'fig04.png'),dpi=600); plt.close(fig)
# 图7：两平台逐次飞行成功率（共有 39 个任务）
fig,ax=plt.subplots(figsize=(5.2,2.6))
names=['UAV-iDP3','Proposed','EGO-Planner(-Swarm)','Fast-Planner kino','SUPER']
for i,(r,nm) in enumerate(zip(f7,names)):
    y=len(f7)-1-i; a,b=r['运动学%'],r['Gazebo%']
    ax.annotate('',xy=(b,y),xytext=(a,y),arrowprops=dict(arrowstyle='-|>',color='#9a9890',lw=1.2,shrinkA=4,shrinkB=4))
    ax.scatter([a],[y],s=42,facecolor='#fcfcfb',edgecolor='#2a78d6',linewidth=1.6,zorder=3)
    ax.scatter([b],[y],s=42,color='#eb6834',edgecolor='#fcfcfb',linewidth=1.2,zorder=3)
    ax.text(max(a,b)+2,y,f'{b-a:+.1f}',va='center',fontsize=8,color='#0b0b0b')
ax.set_yticks(range(len(f7))); ax.set_yticklabels(names[::-1]); ax.set_xlim(20,85)
ax.set_xlabel(f'Flight success rate on the {len(common)} shared tasks (%)'); ax.grid(axis='x',color='#e6e5e0',linewidth=0.6); ax.set_axisbelow(True)
ax.scatter([],[],s=42,facecolor='#fcfcfb',edgecolor='#2a78d6',linewidth=1.6,label='Kinematic (5 flights/task)')
ax.scatter([],[],s=42,color='#eb6834',label='Gazebo/PX4 (2 flights/task)')
ax.legend(loc='lower center',bbox_to_anchor=(0.45,1.0),ncol=2,frameon=False,fontsize=7.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG,'fig07.png'),dpi=600); plt.close(fig)
print(json.dumps({k_:R[k_] for k_ in ['表6','图7','训练曲线_第二阶段','UAV-iDP3_运动学到Gazebo_共有任务','Gazebo转移_UAV-iDP3_本文方法','运动学飞行结局_UAV-iDP3','运动学飞行结局_本文方法']},ensure_ascii=False,indent=0))

# ---------- v14 图4：按 UAV-iDP3 任务结局分组的本文方法成功率 ----------
FIG14=os.path.join(ROOT,'图表','v14'); os.makedirs(FIG14,exist_ok=True)
groups=[('Overall',None),('Sparse','稀疏'),('Moderate','适中'),('Dense','密集')]
cats=[('成功','Previously successful','#2a78d6'),('超时','Previously timed out','#6250d6'),('碰撞','Previously collided','#eb6834')]
fig,ax=plt.subplots(figsize=(6.0,2.6)); w=0.26; vals={}
for gi,(gl,d) in enumerate(groups):
    t=R['转移_UAV-iDP3_本文方法'][d]
    for ci,(src,lab,col) in enumerate(cats):
        n=sum(t[f'{src}->{x}'] for x in ['成功','碰撞','超时']); v=100*t[f'{src}->成功']/n
        vals[f'{gl}_{src}']=round(v,1)
        x=gi+(ci-1)*w
        ax.bar(x,v,width=w*0.92,color=col,label=lab if gi==0 else None)
        ax.text(x,v+1.5,f'{v:.0f}',ha='center',va='bottom',fontsize=7.5,color='#0b0b0b')
ax.set_xticks(range(4)); ax.set_xticklabels([g for g,_ in groups]); ax.set_ylim(0,112); ax.set_yticks([0,25,50,75,100])
ax.set_ylabel('Success rate of Proposed (%)'); ax.grid(axis='y',color='#e6e5e0',linewidth=0.6); ax.set_axisbelow(True)
ax.legend(loc='lower center',bbox_to_anchor=(0.5,1.0),ncol=3,frameon=False,fontsize=7.5,title='Task outcome of UAV-iDP3',title_fontsize=7.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG14,'fig04.png'),dpi=600); plt.close(fig)
R['图4_v14']=vals; json.dump(R,open(os.path.join(OUT,'ch4_numbers.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1,default=str)
print(vals)
