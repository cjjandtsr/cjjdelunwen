# RL调试教学与经验归档

检索日期：2026-10-13。原件URL、字节数、SHA256、成功状态见`inventory.json`。本目录资料是教学/作者经验/源码，不计入原32篇论文。

| 文件 | 来源、用途与相关性 |
|---|---|
| SB3_rl_tips.html | SB3官方教学；信息、终止、简单任务和评价wrapper，直接相关；普通控制数值/动作变换不直接迁入 |
| SpinningUp_research.html | 官方研究教学，Joshua Achiam，2018；消融及完整报告方法，方法相关，不替代数据 |
| AndyJones_rl_debugging.html | Andy Jones第一手调试经验，2021；分组件小问题定位，高方法相关；不是UAV原因发生率或普适数值门槛 |
| ICLR37_PPO_details.html | ICLR Blog Track作者技术文，2022；实际PPO优势/target/batch细节，高实现相关；不当作本项目归一化必错证据 |
| Gymnasium_time_limits.html | Farama官方教学；期限与外部截断/剩余时间/bootstrapping，高语义相关 |
| CleanRL_ppo_continuous_action.py.txt | GitHub插件实际完整文件，blob b454521b6e4a08d4a2f5ecec405132776f5e79eb；第275行批优势与280行loss；第221行合并term/trunc，须明确其与项目规则差别，不作为活动源码 |

引用用途及项目判断见`论文/研究报告/2026-10-13_RouteA_Reward主因假设与其他退化原因_调试资料补充_v1_0.md`。当前训练/源码未改。
