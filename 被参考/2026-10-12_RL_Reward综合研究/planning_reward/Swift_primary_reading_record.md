# Swift 原文阅读记录（PDF下载失败，保留来源和方法定位）

- 检索日期：2026-10-12。
- 原文：Kaufmann et al., Champion-level drone racing using deep reinforcement learning, Nature 620:982–987, 2023-08-30。
- DOI/URL：https://doi.org/10.1038/s41586-023-06419-4；https://www.nature.com/articles/s41586-023-06419-4。
- 实际读取渠道：出版社搜索索引返回正文 The Swift system、Discussion、Methods/Observations/actions/rewards（式7–10）、Code availability；直接页面再次open被nature身份跳转阻断。
- 原件限制：作者PDF URL https://rpg.ifi.uzh.ch/docs/Nature23_Kaufmann.pdf 请求长期停滞，已取消；publisher PDF及HTML请求遭远端连接关闭。没有取得完整PDF，不将本记录标为完整网页或PDF原件。

## 方法读点（概述，不复制整篇正文）

on-policy PPO控制推力和body rates；位置/视觉/门信息来自VIO、门检测、地图和Kalman融合。当前门距离差、感知角度、命令变化/角速度和真实crash构成奖励。训练使用真实数据估计感知与动力学残差。竞速真机结果不等于未知静态障碍到达。

进展式：$r_t^{prog}=\lambda_1(d_{t-1}^{Gate}-d_t^{Gate})$；总式：$r_t=r_t^{prog}+r_t^{perc}+r_t^{cmd}-r_t^{crash}$。碰撞式给出5.0（触地或撞门），正文还说明predefined bounding box。它是逐步门目标进展，不是历史best幅度预算。

完整训练source未公开，只有 https://doi.org/10.5281/zenodo.7955278 的官方伪代码与比赛数据。当前材料没有下载或执行该伪代码。Discussion指出未训练碰撞后恢复，环境外观变化可能导致感知失败。

本阅读记录由Codex在已实际读取的出版社方法基础上整理，用于追溯，不代替原文。
