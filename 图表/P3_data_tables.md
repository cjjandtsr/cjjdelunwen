# P3完整数据附表

编号P为冻结状态顺序；N为新任务顺序；T为旧开发任务编号。均不是训练seed。

## 共同初态全部24状态

| P | 状态ID | T | 来源策略 | 原decision | 分组 | BC到达/5 | u32到达/5 | 新增 | 流失 |
|---:|---|---:|---|---:|---|---:|---:|---:|---:|
| 1 | b7da81109841efaf | 8 | rl_2f3f9914db78_u384 | 23 | mechanism/delayed_after_near_goal | 0 | 0 | 0 | 0 |
| 2 | 4b26c3526db43903 | 56 | rl_2f3f9914db78_u384 | 22 | mechanism/delayed_lost_early_ability | 0 | 4 | 4 | 0 |
| 3 | d35eee463c5a8d86 | 49 | rl_2f3f9914db78_u384 | 2 | mechanism/delayed_ground | 0 | 0 | 0 | 0 |
| 4 | da566faaa44b6acf | 76 | rl_2f3f9914db78_u384 | 4 | mechanism/safe_tail_arrival_cancelled | 5 | 0 | 0 | 5 |
| 5 | 31a279a77008d8c7 | 6 | rl_2f3f9914db78_u384 | 25 | mechanism/whole_plan_failure | 0 | 5 | 5 | 0 |
| 6 | d618c2b0ad079964 | 30 | rl_2f3f9914db78_u32 | 41 | mechanism/successful_bypass_control | 5 | 5 | 0 | 0 |
| 7 | fd518a9f480ec772 | 3 | bc | 21 | post_bypass/success | 5 | 5 | 0 | 0 |
| 8 | af66deb66e0a93b1 | 28 | rl_2f3f9914db78_u32 | 19 | post_bypass/success | 5 | 5 | 0 | 0 |
| 9 | 3f6792cd427a08e7 | 30 | rl_2f3f9914db78_u32 | 42 | post_bypass/success | 5 | 5 | 0 | 0 |
| 10 | f4b0cfee3517898a | 41 | bc | 12 | post_bypass/failure | 0 | 0 | 0 | 0 |
| 11 | a9af069194ed0ef6 | 10 | rl_2f3f9914db78_u32 | 17 | post_bypass/failure | 0 | 0 | 0 | 0 |
| 12 | 925a65bd1e5a83fe | 78 | rl_2f3f9914db78_u384 | 31 | post_bypass/failure | 0 | 0 | 0 | 0 |
| 13 | d86ae61882dd3d65 | 68 | bc | 32 | ground_direct/success | 5 | 0 | 0 | 5 |
| 14 | b9d4971a4c53f989 | 64 | rl_2f3f9914db78_u32 | 24 | ground_direct/success | 1 | 5 | 4 | 0 |
| 15 | c216783315e3df93 | 4 | rl_2f3f9914db78_u384 | 22 | ground_direct/success | 0 | 3 | 3 | 0 |
| 16 | f9979a35dc852fb2 | 27 | bc | 20 | ground_direct/failure | 0 | 0 | 0 | 0 |
| 17 | e90cc62e31cd2c27 | 21 | rl_2f3f9914db78_u32 | 10 | ground_direct/failure | 0 | 0 | 0 | 0 |
| 18 | 83c4de62cff19c71 | 8 | rl_2f3f9914db78_u384 | 17 | ground_direct/failure | 0 | 0 | 0 | 0 |
| 19 | 3c64006b188e82ea | 80 | bc | 4 | visible_clear/success | 5 | 0 | 0 | 5 |
| 20 | c6180527873de062 | 77 | rl_2f3f9914db78_u32 | 8 | visible_clear/success | 0 | 0 | 0 | 0 |
| 21 | da97c35906e9ffd5 | 13 | rl_2f3f9914db78_u384 | 4 | visible_clear/success | 5 | 4 | 0 | 1 |
| 22 | 520e4c7ecef46c51 | 71 | bc | 4 | visible_clear/failure | 0 | 0 | 0 | 0 |
| 23 | dde3e48215b8ff45 | 8 | rl_2f3f9914db78_u32 | 4 | visible_clear/failure | 0 | 0 | 0 | 0 |
| 24 | 55ceb27af0cf4ac3 | 80 | rl_2f3f9914db78_u384 | 4 | visible_clear/failure | 5 | 0 | 0 | 5 |

## 新任务全部24项

结局顺序为到达/碰撞/超时，各策略每任务合计5。

| N | task_id | 世界 | 直连受阻 | 已见几何 | BC结局 | u32结局 |
|---:|---|---|---|---|---|---|
| 1 | 7c052dfbb496a01ea507f1c0 | routeA_rl_v1__anticipatory__rl_test__front_offset_obstacle__000003 | True | False | 5/0/0 | 0/0/5 |
| 2 | 12035adb9dc9b459478a8934 | routeA_rl_v1__anticipatory__rl_test__front_offset_obstacle__000003 | False | False | 0/0/5 | 0/0/5 |
| 3 | a43f7aa883d9594151087f14 | routeA_rl_v1__dense_recovery__rl_test__bottleneck_corridor__000018 | True | False | 0/5/0 | 0/5/0 |
| 4 | f5863dad06de8fe5a1110d2e | routeA_rl_v1__dense_recovery__rl_test__bottleneck_corridor__000018 | False | False | 1/0/4 | 0/0/5 |
| 5 | 2e5eba878003585f9a16fe87 | routeA_rl_v1__dense_recovery__rl_test__bottleneck_corridor__000031 | True | False | 0/5/0 | 0/5/0 |
| 6 | aec1f198c6220a08322f5342 | routeA_rl_v1__dense_recovery__rl_test__bottleneck_corridor__000031 | False | False | 0/3/2 | 0/0/5 |
| 7 | f700ab2c66cacd70678dc43c | routeA_rl_v1__dense_recovery__rl_test__bottleneck_corridor__000032 | True | False | 0/4/1 | 0/5/0 |
| 8 | c770630bc78ce33d4b755f0d | routeA_rl_v1__dense_recovery__rl_test__bottleneck_corridor__000032 | False | False | 0/0/5 | 5/0/0 |
| 9 | 89d02995a38f6e4c57526aa1 | routeA_rl_v1__dense_recovery__rl_test__cul_de_sac_trap__000021 | True | False | 0/4/1 | 5/0/0 |
| 10 | a1ea1b546bc24d5491189908 | routeA_rl_v1__dense_recovery__rl_test__cul_de_sac_trap__000021 | False | False | 0/5/0 | 0/0/5 |
| 11 | 19a505e78b8437469adee341 | routeA_rl_v1__dense_recovery__rl_test__cul_de_sac_trap__000039 | True | False | 0/0/5 | 0/2/3 |
| 12 | d64d00471148258a8e0ee812 | routeA_rl_v1__dense_recovery__rl_test__cul_de_sac_trap__000039 | False | False | 5/0/0 | 5/0/0 |
| 13 | ca3e19cb837104b4b500a302 | routeA_rl_v1__dense_recovery__rl_test__cul_de_sac_trap__000040 | True | False | 0/0/5 | 5/0/0 |
| 14 | 874ef4d72d1e23bbb39b0e12 | routeA_rl_v1__dense_recovery__rl_test__cul_de_sac_trap__000040 | False | False | 0/0/5 | 0/0/5 |
| 15 | 7e4f3b3d3688c0b9eb561854 | routeA_rl_v1__dense_recovery__rl_test__s_turn_multi_obstacle__000024 | True | False | 0/3/2 | 0/1/4 |
| 16 | e1dec665c5069b05de96be6c | routeA_rl_v1__dense_recovery__rl_test__s_turn_multi_obstacle__000024 | False | False | 0/5/0 | 0/0/5 |
| 17 | 7de97d785ca4ba8c1ac24533 | routeA_rl_v1__dense_recovery__rl_test__s_turn_multi_obstacle__000047 | True | False | 1/3/1 | 1/0/4 |
| 18 | f22d0b34391630f2ce1f74ed | routeA_rl_v1__dense_recovery__rl_test__s_turn_multi_obstacle__000047 | False | False | 0/0/5 | 5/0/0 |
| 19 | 0ad2dca145cd0c1e6a8c5dd2 | routeA_rl_v1__dense_recovery__rl_test__s_turn_multi_obstacle__000048 | True | False | 0/5/0 | 0/5/0 |
| 20 | 6bc6ceb11a498f34f9b48e08 | routeA_rl_v1__dense_recovery__rl_test__s_turn_multi_obstacle__000048 | True | False | 0/0/5 | 0/5/0 |
| 21 | cc060ca469d1c0138c5fe307 | routeA_rl_v1__support_expansion__rl_test__mixed_3d_low_density_route__000011 | True | False | 5/0/0 | 0/0/5 |
| 22 | 452ac3262f53f5537fc63273 | routeA_rl_v1__support_expansion__rl_test__mixed_3d_low_density_route__000011 | False | False | 0/5/0 | 0/0/5 |
| 23 | 3c5d1ed686fe9a319af6d86a | routeA_rl_v1__yaw_lateral_recovery__rl_test__initial_yaw_offset_corridor__000015 | True | True | 0/4/1 | 0/5/0 |
| 24 | 955e0d4456052ca29d7da23a | routeA_rl_v1__yaw_lateral_recovery__rl_test__initial_yaw_offset_corridor__000015 | False | True | 5/0/0 | 0/0/5 |
