# 三份RL报告综合审查来源记录

检索日期：2026-10-14。范围：两份用户docx及粘贴文本的关键方法/引用核验，复用项目已有文献；不是重新独立阅读所有报告的全部参考文献。新资料直接保存到现有`论文/被参考/`。

| 来源 | URL / 标识 | 阅读范围、用途及边界 |
|---|---|---|
| DPPO / 官方loss | https://arxiv.org/html/2409.00588v3 ; https://github.com/irom-princeton/dppo/blob/main/model/diffusion/diffusion_ppo.py | 复用既有原件，并本轮核loss关键调用；clamp/mean、归一化/去噪折扣、horizon切片。BC53%饱和对照为Gaussian baseline，不是扩散actor消融 |
| Agile Flight | https://arxiv.org/html/2403.12203v3 | 复用既有PDF/TXT；核方法、§4.2/Fig5及reward附录，支持无人机IL→RL先升后退化类比，不当项目根因证明 |
| Pardo time limits | https://arxiv.org/html/1712.00378v4 | 复用已有PDF与既有2026-09-20核验，区分任务期限与采样截断 |
| Ng PBRS | https://people.eecs.berkeley.edu/~russell/papers/icml99-shaping.pdf | 复用已存原论文；结合2026-09-03/10-14推导，核边界及非线性clip，不向神经DPPO扩展为收敛保证 |
| FDPP | https://arxiv.org/html/2501.08259v1 | 复用已存PDF/HTML；核§IV-C/V-C/V-D，偏好任务中KL与原能力权衡；其原任务未进入偏好reward |
| FLaRe | https://arxiv.org/html/2409.16578v1 ; https://github.com/JiahengHu/FLaRe | 本轮方法/消融及官方ObjectNav入口关键参数；机器人微调稳定机制。当前已具备的低LR/零entropy/独立AC不列为缺项 |
| Policy Decorator | https://arxiv.org/html/2412.13630v1 ; https://github.com/tongzhoumu/policy_decorator | 核§4/§5.4.1及B.4.2；执行动作处理为DIPO基线，不能证明DPPO H8错误。动作编辑框架不直接迁入 |
| EXPO | https://arxiv.org/html/2507.07986v2 ; https://github.com/pd-perry/EXPO | 核方法与实验，SAC式edit/Q选动作；参考base与价值学习分工，不当现成LoRA DPPO修复 |
| Fine-Tuning without Performance Degradation | https://arxiv.org/html/2505.00913v1 | 核题名/作者/假设与related work；第三类为overestimation，非报告写的探索不足；非本项目因果证明 |
| Temporal Self-Imitation | https://arxiv.org/html/2606.19752v1 | 核身份及方法主题；正确编号不是2609.xxxxx，主题不支持所引价值归一化细节 |
| Octo forgetting机构页 | https://digital.library.adelaide.edu.au/items/109fd598-ac57-4af0-b202-9dab9159b405 | 子审查核机构摘要/DOI定位，未通读全文；根侧网页内容未展开、本地下载失败，未伪称保存原件。报告DOI占位不能作为完成核验 |

## 本轮新保存资料

| 文件 | 字节 | SHA256 |
|---|---:|---|
| FLaRe_2409.16578v1.html | 204242 | `da40d8124e4e0411df85381b9e4a786cb2961c4af64b88a7931618681cfe02c5` |
| PolicyDecorator_2412.13630v1.html | 353135 | `1d20f8021a586cd3369584705292f8992bd927b9c8b3106b64acbc32ca2c6f8a` |
| EXPO_2507.07986v2.html | 192776 | `d82c340c3a03cddb1ba5133641acbb24ff69b6c1c621e3e055aa8030e6300939` |
| FineTuningWithoutDegradation_2505.00913v1.html | 321447 | `7f4c7960d13c1747af3353e1361818a904f338e57c28fbc0059d9acf3f9dc128` |
| TemporalSelfImitation_2606.19752v1.html | 312386 | `5983709064f54285de041cb12b20b60411a997c749eb1221828697e73c967f18` |

项目原始数据结论来自现有验收/研究记录，不由这些文献替代。三份新报告共用项目上下文，不能计为三次独立实验。研究材料没有成为执行代码或训练数据。
