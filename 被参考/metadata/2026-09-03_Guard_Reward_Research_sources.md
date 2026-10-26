# 2026-09-03 Guard安全—效率权衡资料归档

- 检索/归档日期：2026-09-03。
- 对应报告：论文/研究报告/2026-09-03_Guard安全效率权衡_论文与开源复核.md。
- 范围：三组实际用于结论的作者论文/官方源码，未下载完整项目，不执行其中程序。
- 根目录：论文/被参考/2026-09-03_Guard_Reward_Research/。
- 保存方式：GitHub连接器获取固定commit的源码文本，经UTF-8/LF规范化、保留文本内容，使用apply_patch归档为.txt。SHA256标识本地副本，不是Git blob hash或原HTTP响应字节hash。
- 论文归档为网页文本提取结果，不是完整PDF或原始HTML；含工具引用标记及选定章节。没有声称完成PDF版式核对。
- 本机PowerShell/curl HTTPS获取遇到TLS凭据错误；已改用只读GitHub连接器和网页工具完成，不更改系统证书、不禁用TLS验证。

## 资料身份与用途

### S1 NavRL

- 标题：NavRL: Learning Safe Flight in Dynamic Environments。
- 作者：Zhefan Xu, Xinming Han, Haoyu Shen, Hanyu Jin, Kenji Shimada。
- 年份：2024预印本；核对2025-02-23修订v2，IEEE RA-L 2025。
- arXiv：2409.15634v2；DOI（arXiv）：10.48550/arXiv.2409.15634。
- 论文：https://arxiv.org/html/2409.15634v2 。
- 仓库：https://github.com/Zhefan-Xu/NavRL 。
- 文件：isaac-training/training/scripts/env.py。
- commit：be785557dcea4ffc03f6fc8d47a9d71b208966a8；该文件最新提交查询日期为2025-04-01T02:32:00Z。
- 固定源码：https://raw.githubusercontent.com/Zhefan-Xu/NavRL/be785557dcea4ffc03f6fc8d47a9d71b208966a8/isaac-training/training/scripts/env.py 。
- 本地：NavRL_env_be785557.txt。
- SHA256：4BE2ED2868A13362CBD7645254ADE281C478F64000BE163CA11A907E6D2A9B7D。
- 用途：核对安全/进展/平滑分项直接加总；确认存在不能照搬的高度终止。
- 迁移边界：不复制安全盾、高度上限、正存活bonus，不把此实现视为本项目guard参数的验证。

### S2 Aerial Gym Simulator

- 标题：Aerial Gym Simulator: A Framework for Highly Parallelized Simulation of Aerial Robots。
- 作者：Mihir Kulkarni, Welf Rehberg, Kostas Alexis；代码含项目贡献者。
- 年份：论文2025；本次固定代码提交2026-02-04T13:09:07Z。
- arXiv：2503.01471；DOI（arXiv）：10.48550/arXiv.2503.01471。
- 论文身份：https://arxiv.org/abs/2503.01471 。
- 仓库：https://github.com/ntnu-arl/aerial_gym_simulator 。
- 文件：aerial_gym/task/lidar_navigation_task/lidar_navigation_task.py。
- commit：74963fde8a758b2c277cdecdcd25e776f01fd9ce。
- 固定源码：https://raw.githubusercontent.com/ntnu-arl/aerial_gym_simulator/74963fde8a758b2c277cdecdcd25e776f01fd9ce/aerial_gym/task/lidar_navigation_task/lidar_navigation_task.py 。
- 本地：AerialGym_lidar_navigation_74963fde.txt。
- SHA256：0FC2AE65D8BB97C5DCA466F2ADBFB05DEDF66A0E3006F154C34455F044B52270。
- 用途：核对根据航向误差门控低角速度偏好的实现；近目标上下文不可省略。
- 迁移边界：正奖励门控不等于负惩罚豁免；只作为情境调节的实现案例，未独立复现。

### S3 Adaptive Safety Margins

- 标题：Learning Adaptive Safety Margins for Visual Navigation。
- 作者：Junyi Hu, Shuaihang Yuan, Geeta Chandra Raju Bethala, Anthony Tzes, Yi Fang。
- 年份：2026；arXiv v1日期2026-07-20。
- arXiv：2607.18200v1；DOI（arXiv）：10.48550/arXiv.2607.18200。
- 论文：https://arxiv.org/html/2607.18200v1 。
- 作者项目页：https://junyi2005.github.io/safety-critic/ （自报IROS 2026 accepted；不据此声称独立出版认证）。
- 仓库：https://github.com/junyi2005/safety-critic 。
- 文件：navdp_safety/models/scorer.py。
- commit：5b3e94d2c11ee175d96005d2b1fb1c80e6b51334；该文件提交时间2026-07-15T07:00:04Z。
- 固定源码：https://raw.githubusercontent.com/junyi2005/safety-critic/5b3e94d2c11ee175d96005d2b1fb1c80e6b51334/navdp_safety/models/scorer.py 。
- 本地：SafetyCritic_scorer_5b3e94d2.txt。
- SHA256：9EB6584FC1AF6BF8FF5BEBCDEA08A0DE2B8452883535EF8D4F0296D6E9576857。
- 用途：核对安全门控绕路比的式(7)–(8)及_gated_detour实现。
- 迁移边界：平面候选评分，不是3D DPPO；不迁移selector/CBF/可学习margin；全效率项消融不等于门控函数单独消融。
- 授权提示：仓库标明CC BY-NC 4.0；论文HTML标明CC BY-SA 4.0。本轮作非商业研究资料引用；若后续复制代码需另行遵循许可证。

### S1/S3论文网页提取快照

- 本地：Paper_web_extracts.json。
- 内容：上述两个arXiv HTML的已访问方法/消融文本提取。
- SHA256：DA4996F77B96D6D087EFDAEE9D5256E1CCEC9986350839D8BEABA9A9E6D56A7E。
- 边界：不声称包含完整原文资源、图像、PDF或原始HTML；准确公式与实现通过原文和固定源码交叉核对。

## 证据强度

[FACT] 归档证明存在这些公式/实现，不证明本项目采用后训练会更好。

[JUDGMENT] 用于推荐安全情境门控下的独立加总，不用于替v1.3的Delta_d/d_cap免罚式提供未经验证的论文背书。检索到但未用于结论的其他资料只留在报告候选表。
