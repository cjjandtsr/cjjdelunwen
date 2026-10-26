# 障碍相对高度 Reward 研究来源清单

| 字段 | 内容 |
|------|------|
| 检索日期 | 2026-09-02 |
| 检索主题 | UAV obstacle-relative clearance, excessively high flight penalty, fly-over-or-around, climbing energy |
| 配套报告 | `论文/研究报告/2026-09-02_障碍相对高度与爬升惩罚Reward研究.md` |

## 已归档来源

| 本地文件 | 来源与用途 | URL / DOI | SHA256 |
|----------|------------|-----------|--------|
| `Li_Yang_2026_RL_Driven_UAV_Terrain_Clearance.pdf` | 相对地形净空、最低/期望净空、超额高度二次代价；核心公式证据 | https://doi.org/10.3390/biomimetics11070470 | `7920458AD18901A754B8F7B193FD1258195ECA32B309408CA6C3ADEC72139C42` |
| `Lee_2023_Terrain_Following_Desired_Clearance_MPC.pdf` | $h_r=h_t+h_c$ 与净空跟踪二次代价；参考高度构造依据 | https://doi.org/10.13009/EUCASS2023-532 | `461937DD911863E18AAD732ED10D11EBAEA3642CE54CA177D17B84302D2353C1` |
| `Qi_2025_Multi_UAV_Climbing_Energy.pdf` | $Mg\max(\Delta h,0)/\eta$ 爬升能耗模型；垂直运动代价物理依据 | https://doi.org/10.1038/s41598-025-99001-z | `804CAFD8EB95D12E46362D09CC1BE2639D1C55460C7589B244769FF64CEB8F62` |
| `Bouhamed_2020_DDPG_UAV_Fly_Over_Or_Around.pdf` | DDPG 学习三维飞越/绕行；行为可行性与连续 crash-depth reward | https://arxiv.org/abs/2003.10923 | `C15BE3D9EAAB9D5E6AA0FDA228F284C2458EEF4864257634397F159C56741257` |
| `Jin_2026_Fly_Over_Or_Around_source.html` | 出版商页面快照；密集高楼中飞越/绕行与爬升能耗问题定义 | https://doi.org/10.1016/j.pmcj.2025.102156 | `D869ED9854F3059936BDE53AB1ACE8CCA65BFD8262CB02B149215F84673BC9E9` |
| `Liu_2026_GRPO-MDP_Alexandria_Engineering_Journal.pdf` | soft-CBF 连续安全惩罚；只迁移软屏障思想 | https://doi.org/10.1016/j.aej.2026.02.024 | `3C9C3CD72B0BA48292235291E6E037A4AE6A1A45ABEC4D063D7541675F7EA266` |

## 证据边界

- Li 与 Yang 2026、Lee 等 2023、Qi 等 2025、Bouhamed 等 2020 均已读取原文并核对关键公式页。
- Jin 等 2026 只保存出版商官方页面快照；全文不可公开获取，因此不引用其未公开公式或权重。
- 所有论文数值均属于各自平台和地图尺度，不直接迁移到 iDP3-UAV。
- 不采用候选路径 repair、QP safety filter 或其他推理后轨迹修剪。
