# Route A R5 官方/主流 PPO 来源快照 Manifest

| 字段 | 内容 |
|------|------|
| 下载日期 | 2026-08-15 |
| 下载方式 | 按文件串行下载；每个文件完成后立即 SHA256 校验 |
| 范围 | 只保存本次审查实际使用的上游源码/文档；不重复下载完整 DPPO 仓库 |
| DPPO 冻结 commit | `cc7234ad7ff39a8f32de3af903606723a16f0648` |

## 文件与校验

| 本地文件 | 字节 | SHA256 | 上游 URL |
|----------|-----:|--------|------------|
| `dppo_train_ppo_diffusion_agent_cc7234a.py` | 22160 | `C21BB92690D4EB36846CB4550E8FFC946CB4E5D5B33E190D9B35E1CA66E235DB` | https://raw.githubusercontent.com/irom-princeton/dppo/cc7234ad7ff39a8f32de3af903606723a16f0648/agent/finetune/train_ppo_diffusion_agent.py |
| `dppo_diffusion_ppo_cc7234a.py` | 7140 | `E6071BB23B426B0C75E347CCDE71BB91E3A572DE0B17F0A28FA294DC3F3CA563` | https://raw.githubusercontent.com/irom-princeton/dppo/cc7234ad7ff39a8f32de3af903606723a16f0648/model/diffusion/diffusion_ppo.py |
| `dppo_README_cc7234a.md` | 14801 | `0142172864DD6248D4FD563BB5AC2C01435DFEBF18B2D6FDD27DDCBFB141EB3D` | https://raw.githubusercontent.com/irom-princeton/dppo/cc7234ad7ff39a8f32de3af903606723a16f0648/README.md |
| `cleanrl_ppo_continuous_action_master_20260815.py` | 14933 | `326DD8678BF9CC51ABEC833EB551EF2409A3804D604B689E1F0A084ECA41F655` | https://raw.githubusercontent.com/vwxyzjn/cleanrl/master/cleanrl/ppo_continuous_action.py |
| `sb3_on_policy_algorithm_master_20260815.py` | 14576 | `CE1984EA8E8A2D969443A484AB159194B9D70FF92A7EF1BC25FCC183E391E35C` | https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/stable_baselines3/common/on_policy_algorithm.py |
| `sb3_buffers_master_20260815.py` | 40735 | `21DB27F000048615F5848FACF18AF9AFC22E6E2A1C26148911C2CBA542D1988D` | https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/stable_baselines3/common/buffers.py |
| `openai_spinningup_ppo_20260815.html` | 44089 | `B60B15FE9663F95A217A6B6BF9C1389984A1D8520E13BD0690D0F104DD93E97E` | https://spinningup.openai.com/en/latest/algorithms/ppo.html |
| `gymnasium_handling_time_limits_20260815.html` | 48104 | `6A4B59D216B2722F83F218F445B39DEF5A2433CC68E5381DA10EC5F842688F86` | https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/ |

## 边界

[FACT] WSL 执行仓库已存在冻结 DPPO vendor 401 文件，本目录不是第二份可执行 vendor，只是审查引用快照。

[JUDGMENT] CleanRL 和 SB3 快照使用 2026-08-15 的 upstream `master`，因此必须以本 manifest 的 SHA256 而不是未来 `master` 指针作为本次审查引用真值。
