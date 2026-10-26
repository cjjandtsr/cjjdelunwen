# 六篇网络文章与非RL架构路线：来源记录

检索日期：2026-10-15。报告：`论文/研究报告/2026-10-15_六篇网络文章与非RL架构路线适配分析_v1_0.md`。

用户要求以微信公众号线索讨论架构替代，不限于论文/GitHub。因此先搜索同题文章、作者博客和公开解读，再核对关键技术。六个微信短链接直接访问均进入验证码，未绕过；作者和摘要来自用户补充，不假装独立读到微信全文。

## 一、六个入口及查到的公开资料

| 编号 / 用户给出的标题 | 微信URL | 实际阅读与验证范围 |
|---|---|---|
| 1. PI：从π0到π*0.6和RLT | https://mp.weixin.qq.com/s/Q1BOx8kZcc8FxfgPpTyTFg | 用户摘要；未核准同名全文。另核PI作者KI、RECAP、RLT网页；不采用摘要中未核准分母的泛化提升数字 |
| 2. 具身智能扎堆流匹配：FM全面取代Diffusion了？ | https://mp.weixin.qq.com/s/Reqadr6Jpp6a1CP9TlCTUw | 找到同题深蓝学院公开版本 https://damodev.csdn.net/6abcd31605257b0857141963.html ，实际正文可读；指出其生成场与物理演化混淆，不把文章宣传当实验结论 |
| 3. 世界模型：FM深度解析 | https://mp.weixin.qq.com/s/QHd-kGwIn0CSVWX1zwVbQA | 用户摘要；未找到已核准同名完整转载。公式按定义分析，FM基础出处另核2210.02747 |
| 4. 不借助机器学习第三方库构建FM模型（一） | https://mp.weixin.qq.com/s/NtraC_5Fd1lgenIeUm2MLA | 用户摘要；未找到已核准同名完整转载。玩具生成不能作为UAV对照，纠正ε唯一预测、整数时间和必然少步等绝对说法 |
| 5. 生成候选只是真实闭环的一部分 | https://mp.weixin.qq.com/s/fd2vqBg_7oUj4BvIGyv-Uw | 找到同作者《从随机动作块到真实闭环：Diffusion与Flow策略的执行账本》https://blog.51cto.com/wuzikang/14841413 ，搜索正文可读；直接打开cache miss，下载未取得完整正文，未保存伪原件 |
| 6. ICLR2026：GRPO在扩散模型上根本行不通？ | https://mp.weixin.qq.com/s/qar_9AOY0rqrh43gahNMrg | 用户摘要；GenMind https://genmind.org/?post=b11 搜索可读其解读片段，动态页直接打开无正文；另核作者项目和ICLR2026题名。ESPO是2512.03759，不是2512.00499的同名缩写 |

## 二、实际使用的作者解读与理论资料

| URL / 标识 | 引用用途 | 本项目限制 |
|---|---|---|
| https://www.pi.website/research/knowledge_insulation ; 2505.23705 | stop-gradient同时为VLM提供FAST等替代监督，区别于单纯全冻结 | 本项目不是VLM，已有冻结也非完整KI |
| https://www.pi.website/blog/pistar06 | π*0.6通过RECAP利用纠正和自主经验 | 不作为放弃RL证据；人工纠正数据不能直接照搬冻结EGO方案 |
| https://www.pi.website/research/rlt ; 2604.23073 | 固定VLA读出表征、小actor/critic与参考行为 | 独立actor直接生成动作，涉及本项目扩散核心与归因边界 |
| https://jingyangou.github.io/ESPO-Demo/ ; 2512.03759 | ESPO方法对象为扩散语言模型，序列ELBO代理，不是连续DPPO | 不迁移其文本得分或k2系数为UAV参数 |
| https://proceedings.iclr.cc/paper_files/paper/2026/hash/0907335ecf28faf15be54485dbcbe70e-Abstract-Conference.html | 独立确认正式题名与会议 | 不把标题“GRPO根本行不通”扩大为所有扩散RL不成立 |
| https://arxiv.org/abs/2210.02747 | FM原始题名与CFM生成概率路径；用于核对数学对象 | 生成τ不同于物理时间；条件直线不保证边际OT或飞行直线 |
| https://arxiv.org/abs/2506.07339 | RTC适用条件与异步衔接 | 不保证恢复/到达；复用既有RTC_2506.07339v2.html |
| https://arxiv.org/abs/2406.04806 | SDP持续噪声缓冲，需要训练与采样改变 | 不当旧E5即插即用；不保证脱困 |
| https://consistency-policy.github.io/ ; 2405.07503 | 区分去噪蒸馏一致性与跨规划周期一致性 | 复用既有ConsistencyPolicy_RSS2024_p071.pdf，不把加速当能力提升 |

## 三、直接保存的来源副本

以下均直接放已有`论文/被参考/`，无新增文献文件夹。HTML为自动下载的来源原件，不用手写摘要替代原文。部分为摘要页而非论文全文，已在文件名和来源URL中区分。

| 文件 | bytes | SHA256 |
|---|---:|---|
| article2_flow_matching_DAMO_20261015.html | 189239 | cd073fc9b4bdc607fac60fb9572a76f3230e238bc7a2e9dd2b56fbe0c5a09c0b |
| PI_knowledge_insulation_20261015.html | 168413 | c4adfe5737e597f92654b676e4137468f82055bc099b747a04b8b3a1d23f23a7 |
| PI_pistar06_RECAP_20261015.html | 210525 | 857fffb1034155ac925f62bcfff124b94345c20bacfdb73d0903d8212382d162 |
| PI_RLT_20261015.html | 171293 | ec8d9f64bfdcca1c6bcba7093589d3a005444be6424f1fa1d2a2f085d9a4a3ac |
| ESPO_author_project_20261015.html | 23230 | 2b9e07a5a7992e642e6bb5a5ba30c40bba030616c014bcfca61d0e0c806d946b |
| FlowMatching_original_2210.02747_20261015.html | 42554 | 228275106e1c6eb485b9729a4226982bd7bb7f5fc8d16fd3d6567aa49074d25d |
| StreamingDiffusionPolicy_2406.04806_20261015.html | 42538 | ec3b99fd5bf1752e1c6d9aa8313393d5870fd89d066bd04cccede98f8a6a42ac |

## 四、源码核查与旧报告纠正

当前E5的DDIM/x0分支、评价deterministic与训练随机Gaussian链已对照实际源码和fresh快照；旧报告称“当前DDPM需先切DDIM才能研究DSRL”不准确，已在原报告和原metadata原位标记纠正。没有更改实验原件、训练/评价程序或权重。

当前multi-stage PointNet还由fresh训练日志第5行确认；不是只由预设合同或目录名猜测。2026-10-15后续已取得native policy、dataset与BC训练workspace，并核实与A0/R1回传归档一致；当前native loss仅扩散MSE、不消费prev_action。归档中又找到checkpoint完整cfg的原始探针日志；但8月16日实际训练入口/源码与日志仍未绑定，不能将当前可见训练函数直接当成历史训练全部事实。详见`jindu/2026-10-15_当前基座与全链路代码审计_v1_0.md`。

2026-10-15同日用户进一步提供WSL定位报告：E5日志有非零collision分项，训练为独立train_phase1a入口。随后本轮已从A0/R1原始tar读到入口全文，核实独立构造Phase1aPolicy、碰撞项进入总损失和backward、旧cfg原样保存，以及真实val_loader和末段加权采样；并发现编码前3帧、辅助却取第16帧几何的归档实现对齐问题。该次E5原日志及8月时点版本未绑定，不能冒充历史训练独立验收；也不能因native类内只有MSE就判未用辅助。来源、入口SHA与待核事项已写入主审计v1.1，未修改模型或实验原件。

**后续原件已到并复核（同日v1.2，取代上两段“原日志未到”的状态）**：`wsl_snapshot/e5_collision_provenance_20260814/`12文件已读取，README列出的6份源SHA逐个重算一致，5份非空日志合80条均符合total≈bc+collision，anchor恒0，另1份原日志0字节。训练前Git导出的compute_loss与当前一致，body→world修复及总损失反传均存在；已足够支持E5使用过碰撞辅助。对齐风险仍在，但AutoDL启动时dataset/完整执行源码hash未回传，不能把Git导出等同运行字节，也不据日志推断闭环收益。统计与所有本地文件hash见`jindu/2026-10-15_E5碰撞辅助原件核验数据.json`，主审计已更新v1.2，无模型行为改动。

## 五、2026-10-16非RL主线讨论补核

检索/复核日期：2026-10-16。用于同报告§9的资源优先级讨论；本次未宣称完成新的全面文献综述。复用既有DPPO论文与官方调参归档、SDP摘要HTML；新增来源副本直接存本目录，没有新建文献文件夹。

| 来源 URL / 标识 | 本轮用途 | 对iDP3-UAV的相关性及边界 |
|----------------|----------|------------------------|
| https://3d-diffusion-policy.github.io/ ; 2403.03954 | 紧凑3D编码、Simple DP3简化U-Net而保留性能，避免更大模型必然更好的推断 | 支持结构对照方法，不是UAV任务的有效性证明 |
| https://github.com/Streaming-Diffusion-Policy/streaming_diffusion_policy ; 2406.04806 | 官方列出策略、scheduler和模型结构均需修改，说明不是给E5换权重即可 | 连续生成和加速可借鉴，不保证恢复/到达 |
| https://arxiv.org/abs/2409.00588 ; https://diffusion-ppo.github.io/ | 原DPPO研究旨在利用预训练策略并通过交互超出示范表现 | 反对由本项目一次实现退化推断所有RL无用；不作为本项目收益证据 |
| https://github.com/irom-princeton/dppo/blob/main/cfg/finetuning.md | 核对官方说明按版本/任务比较与不同骨干配置 | 复用`DPPO_finetuning_cc7234a.md`，网络main不当成当前冻结vendor执行字节 |

| 新增资料副本 | bytes | SHA256 |
|--------------|------:|--------|
| `DP3_author_project_20261016.html` | 65728 | `353145501049c3c5a67fca1a76c19bce9dcc3b904a7b8bdb28c84eac9dbee419` |
| `StreamingDiffusionPolicy_official_README_20261016.md` | 3207 | `480866dc2c6f04ef01290e3dddaa93fade3993aa3b188e0ed858f516836a1624` |

以上是下载的作者原网页/README，不是手写摘要；项目优先级结论为结合本地代码与轨迹后的研究判断，未实施新模块。
