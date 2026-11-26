"""只读：统计 P9、P11（F3@u129–u192）每轮训练记录中的更新幅度指标。
用法：python3 f7_update_size_scan.py <项目仓库根目录>
数据：<根>/jindu/routea_f5_run01/results/prepared/training/{P9,P11}/metrics_update_*.json
字段：formal_training.{actor_learning_rate, optimizer_metric_summary.{approx_kl,clip_fraction,ratio_mean}, rollout_seconds, update_seconds}
"""
import glob, json, os, statistics as st, sys
root = sys.argv[1]
for run in ("P9", "P11"):
    fs = sorted(glob.glob(os.path.join(root, "jindu/routea_f5_run01/results/prepared/training", run, "metrics_update_*.json")))
    kl, cf_max, cf_mean, rmin, rs, us, lr = [], [], [], [], [], [], []
    for f in fs:
        ft = json.load(open(f))["formal_training"]; s = ft["optimizer_metric_summary"]
        kl.append(s["approx_kl"]["mean"]); cf_max.append(s["clip_fraction"]["max"]); cf_mean.append(s["clip_fraction"]["mean"])
        rmin.append(s["ratio_mean"]["min"]); rs.append(ft["rollout_seconds"]); us.append(ft["update_seconds"]); lr.append(ft["actor_learning_rate"])
    print("%s: %d 轮 (%s—%s)" % (run, len(fs), os.path.basename(fs[0])[15:21], os.path.basename(fs[-1])[15:21]))
    print("  approx_kl 每轮均值：中位数 %.2e，最大 %.2e" % (st.median(kl), max(kl)))
    print("  clip_fraction 每轮均值：中位数 %.5f，最大 %.5f；每轮最大值的最大 %.5f；为 0 的轮数 %d" % (st.median(cf_mean), max(cf_mean), max(cf_max), sum(c == 0 for c in cf_mean)))
    print("  ratio_mean 最小值：%.5f" % min(rmin))
    print("  学习率 %.4g → %.4g" % (lr[0], lr[-1]))
    print("  每轮耗时中位数：采集 %.0f s，更新 %.0f s（采集占 %.0f%%）" % (st.median(rs), st.median(us), 100 * st.median(rs) / (st.median(rs) + st.median(us))))
