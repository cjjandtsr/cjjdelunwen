# routea_final_v1.3 交付包（2026-11-07）

本目录含 9 个交付 tar.gz 及各自的 .sha256。其中两个因超过 GitHub 100 MB
单文件硬限被切分为 90 MB 分片，恢复方法：

```bash
cat routea_final_existing_delivery_run06.tar.gz.part* > routea_final_existing_delivery_run06.tar.gz
cat routea_final_stage2_delivery_run03.tar.gz.part* > routea_final_stage2_delivery_run03.tar.gz
sha256sum -c routea_final_existing_delivery_run06.tar.gz.sha256
sha256sum -c routea_final_stage2_delivery_run03.tar.gz.sha256
```

本分支基于本地 ref 7ac855ce（创建时远端主分支 tip 为 67c300bc，因网络
下载故障未能获取）；合并回 paper-v2-restructure 时仅新增 jindu/ 目录，
与主分支无冲突。
