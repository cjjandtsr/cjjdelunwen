# Reward v1.7审查：PBRS理论边界复核

| 字段 | 内容 |
|---|---|
| 检索日期 | 2026-09-03 |
| 类型 | 定向理论复核，非新训练方案 |
| 关联设计 | sheji/Reward_v1_7_ObstacleRelativeHeight_and_ActiveCapability_Design_v1_1.md |
| 项目阶段 | contactfix训练后reward修订；不运行训练、不改源码 |

## 1. 检索范围与来源

仅补查审查Q4涉及的potential-based reward shaping理论。项目当前三类能力目标不变；本次不扩展机器人/UAV对标项目清单。

| 资料 | URL / DOI / arXiv | 用途与状态 |
|---|---|---|
| Ng, Harada, Russell，ICML 1999 | https://www.cs.utexas.edu/~shivaram/readings/b2hd-NgHR1999.html | [FACT] 核验题名、作者、1999年、278–287页；书目页不作为完整证明 |
| Wiewiora，JAIR 19 (2003), 205–208 | https://arxiv.org/abs/1106.5267 ; DOI 10.1613/jair.1190 | [FACT] 原作者论文摘要确认PBRS及Q初始化关系；只引用其适用主题，不据摘要扩展到神经DPPO收敛 |
| Ng论文Berkeley镜像 | https://people.eecs.berkeley.edu/~pabbeel/cs287-fa09/readings/NgHaradaRussell-shaping-ICML1999.pdf | [UNCERTAIN] 本次抓取超时，未冒称已读全文 |
| 旧资料清单所引用Toronto链接 | https://www.teach.cs.toronto.edu/~csc2542h/fall/material/csc2542f16_reward_shaping.pdf | [FACT] 本次返回Toryn Klassen在2016年制作的28页讲义，不是1999原始论文；不作为本轮唯一理论证据，不改写旧档案 |

## 2. 本项目直接推导与源码核对

**[PROVEN]** 同一个环境折扣下，F_t=gamma*Phi_(t+1)−Phi_t有以下恒等式：

$$
\sum_{t=0}^{T-1}\gamma^t F_t=-\Phi_0+\gamma^T\Phi_T.
$$

这是本轮直接代数推导。真正terminal的吸收态Phi_T=0；time-limit截断不能无故删除尾项或换成reset状态。对F本身作非线性clip通常破坏该恒等式；限制Phi再求差不破坏它。

**[FACT]** Windows镜像formal contactfix配置第33行为gamma_environment=0.99，第34行为GAE lambda=0.95，第35行为gamma_denoising=0.8。pipeline.py:298将环境gamma传GAE；env/reward_v13.py:850自行默认0.99、:853做difference clip，environments/kinematic_adapter.py:52-68终止分支覆写dense reward。相关根目录为 chengxu/Improved-3D-Diffusion-Policy/diffusion_policy_3d/rl/dppo_uav_rebuild/。

**[JUDGMENT]** v1.7绑定环境gamma=0.99、只限制potential幅度、保留terminal修正并统一结算；不修改DPPO去噪核心。恒等式只约束PBRS增量，不给全reward最优策略不变、训练必然收敛或安全保证背书。

## 3. 可迁移性与MC边界

本轮使用一般RL reward变换性质，独立于机器人/UAV平台；仅作用训练reward，不修剪轨迹、不重采集数据，不增加推理期特权输入。MC-1～MC-5边界保持。下一步为v1.1定向复核，然后Windows编码、WSL一次确定性核对与replay；没有新增短训。

## 4. 归档

仅保存实际核实的书目/摘要元数据副本，位于 论文/被参考/metadata/2026-09-03_Reward_v17_PBRS_sources.md；本轮未取得原始全文的新本地副本。其他高度设计依据沿用2026-09-02研究报告，不在本轮冒称重新验证。
