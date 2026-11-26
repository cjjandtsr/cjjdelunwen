#!/bin/bash
# 逐目录：稀疏检出 → 整理 → 退出检出（释放工作区）
set -u
R=/home/claude/f7clone; O=/home/claude/clean_out; T=/home/claude/cleanup_tools
cd $R
run() { d=$1; m=$2
  echo "== $(date +%T) $d $m"; git sparse-checkout add "$d" >/dev/null 2>&1; git checkout -q origin/main 2>&1 | tail -1
  du -sh "$d"; python3 -I $T/summarize_run.py $R "$d" $O $m; echo "rc=$?"
}
run jindu/routea_f7_run01 lossless
run jindu/routea_f5_run01 lossless
run jindu/routea_xk_run01 slim
run jindu/routea_test12_independent_run02 slim
run jindu/routea_a2_selective_keep_run01 slim
run jindu/routea_common_a1_v1_run01 slim
echo "ALL DONE $(date +%T)"
