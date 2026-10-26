# BC成功能力保持研究：来源与归档说明

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-10-12，Asia/Shanghai |
| 引用用途 | BC预训练策略经RL微调后的旧能力保持、恢复、拓展；reward与更新机制的区别 |
| 对应研究记录 | `论文/研究报告/2026-10-12_BC成功能力保持与再获得_双向钢人与2020至2026文献复核_v1_0.md` |
| 使用范围 | 文献论证；不构成参数批准，不执行下载的上游程序 |
| 完整性记录 | 本目录两个自动生成inventory记录实际下载URL、状态、字节数、SHA256与固定commit；保留失败记录 |

## 1. 论文、引用用途与项目相关性

| 论文及年份 | 原始来源、标识 | 本地原件 | 本次引用与限制 |
|---|---|---|---|
| AWAC: Accelerating Online Reinforcement Learning with Offline Datasets（2020） | [arXiv:2006.09359](https://arxiv.org/abs/2006.09359)，作者项目https://awacrl.github.io/ | `AWAC_2006.09359v1.pdf` | 持续利用旧经验、优势加权学习；off-policy方法，不能把回放直接接入当前PPO；归档是v1，在线摘要页当前为v6 |
| Efficient Online Reinforcement Learning with Offline Data / RLPD（2023） | [arXiv:2302.02948](https://arxiv.org/abs/2302.02948) | `RLPD_2302.02948.html` | 混合离线与在线训练batch；不等于BC动作模仿，也不是旧成功保证；HTML来自不固定版本URL |
| Imitation Bootstrapped Reinforcement Learning / IBRL（2023） | [arXiv:2311.02198](https://arxiv.org/abs/2311.02198) | `IBRL_2311.02198v1.pdf` | BC与RL动作选择；系统成功须与RL自身能力分开归因 |
| Diffusion Policy Policy Optimization / DPPO（2024，ICLR 2025） | [arXiv:2409.00588](https://arxiv.org/html/2409.00588) | 复用`论文/被参考/metadata/2409.00588v3.pdf`与既有官方代码原件 | 主实验不加固定BC正则；官方代码另有可选BC损失；在线当前HTML与既有v3副本的版本不自动视为相同 |
| FDPP: Fine-tune Diffusion Policy with Human Preference（2025） | [arXiv:2501.08259v1](https://arxiv.org/html/2501.08259v1)，[MERL出版原件](https://merl.com/publications/docs/TR2025-053.pdf) | `FDPP_2501.08259v1.pdf`、同名HTML | 固定预训练策略KL与旧能力保持；其reward未含原任务目标，区别于R1；v1最大化公式正αKL符号需复核；未核实官方代码 |
| Beyond Imitation: Reinforcement Learning Fine-Tuning for Adaptive Diffusion Navigation Policies（2026-03预印本） | [arXiv:2603.12868v1](https://arxiv.org/html/2603.12868v1) | `BeyondImitation_2603.12868v1.html`；PDF复用`论文/被参考/metadata/2603.12868v1.pdf` | 局部2D候选评分、GRPO、局部冻结、无参考KL；不等于当前3D UAV任务；正文所称去KL消融未找到对应开关比较表；未核实官方代码 |
| Immiscible Diffusion Policy: Preserving Multimodal Robot Actions through Label-Free Noise Assignment（2026-10-07预印本） | [arXiv:2610.09369v1](https://arxiv.org/abs/2610.09369v1) | `ImmisciblePolicy_2610.09369v1.pdf`、同名HTML | 监督扩散训练保持动作模式；模式保持与RL旧成功保持不同，不能直接定因R1；未核实官方代码 |

## 2. 官方GitHub源码的实际核查

| 官方项目、文件 | 版本与实际存档 | 核查内容 |
|---|---|---|
| [AWAC / rail-berkeley/rlkit](https://github.com/rail-berkeley/rlkit/tree/master/examples/awac)，`rlkit/torch/sac/awac_trainer.py` | commit `1bfe7d983bbe32c997462a0cfd8aeab20c44e2a4`；`AWAC_awac_trainer.py.txt` | 优势score、softmax/exp权重与加权动作似然；不是只阅读README |
| [RLPD / ikostrikov/rlpd](https://github.com/ikostrikov/rlpd)，`train_finetuning.py` | commit `c90fd4baf28c9c9ef40a81460a2e395092844f88`；`RLPD_train_finetuning.py.txt` | :184-190实际采样旧/在线batch并combine |
| [DPPO / irom-princeton/dppo](https://github.com/irom-princeton/dppo)，`model/diffusion/diffusion_ppo.py` | 复用commit `cc7234ad7ff39a8f32de3af903606723a16f0648`；`论文/被参考/RouteA_R5_official_sources_20260815/dppo_diffusion_ppo_cc7234a.py`；来源记录`论文/被参考/DPPO_Official_Code_cc7234a_metadata.md` | :104-126可选BC损失；当前项目关闭且wrapper未实现该分支 |
| [IBRL / hengyuan-hu/ibrl](https://github.com/hengyuan-hu/ibrl)，[rl/q_agent.py](https://github.com/hengyuan-hu/ibrl/blob/main/rl/q_agent.py) | 2026-10-12在线读取main；未固定commit、未成功保存源码文件 | `_act_ibrl`将BC/RL动作交给critic选择，eval_mode也可选BC；不冒充纯RL执行 |

## 3. 下载失败及已有替代原件

- `RLPD_2302.02948v1.pdf`下载TLS握手超时；已保存对应论文HTML，未声称PDF归档成功。
- AWAC作者项目网页下载连接重置；已在线核查作者链接并保存论文PDF和固定官方训练源码。
- 新取DPPO源码下载连接重置；复用项目既有固定commit官方原件，未新增重复代码副本。
- IBRL源码下载连接重置，后续直接下载又读取超时；已在线读取核心方法并保存论文PDF，未生成假的源码原件。
- 本目录`.py.txt`是研究原件，不是项目活动源码；自动生成PDF/HTML/下载清单由下载器保存，Markdown说明通过结构化补丁写入。

## 4. 同日循环规划与逐轮信用来源补充

| 来源 | 检索日期与原件 | 用途及边界 |
|---|---|---|
| [Gymnasium官方Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/) | 2026-10-12；`Gymnasium_handling_time_limits_20261012.html` | 区分任务本身的有限期限终止与人为采集截断；说明bootstrap为何与原始回合分数不同，不能不核实任务定义就认定是bug |
| [APEX: Learning Adaptive High-Platform Traversal for Humanoid Robots，arXiv:2602.11143v3](https://arxiv.org/html/2602.11143v3) | 2026-10-12；`APEX_2602.11143v3.html`；v3日期2026-08-13 | 对照R1设计已引用的历史最好进展思想；人形接触运动任务与0/−1反馈不等同当前UAV的新记录正增量，不作为可直接移植算法 |

两份HTML均下载成功，实际URL、字节数和SHA256记录于`cycle_reward_sources_inventory_20261012.json`。研究记录§9另包含原2940份BC/R1轨迹的回报重算、task7逐轮反馈、现有reward函数的明确假设路径计算，以及三份原训练metrics的实际读取；假设路径计算不冒充真实模型回放。
