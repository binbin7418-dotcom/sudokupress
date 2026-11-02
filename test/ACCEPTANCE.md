# SudokuPress — 验收记录（ACCEPTANCE）

验收（`test/acceptance_test.py`，真实运行结果见 `test/acceptance_results.txt`）：**8/8 PASS**（总耗时 0.9s）

## 方法与断言

- 方法：先回溯填满完整合法网格，再以 180° 旋转对称对为单位逐对挖洞；每次挖洞后用独立计数求解器（MRV 回溯）数解，解数 ≠1 立即回滚——唯一解由构造保证
- 断言：
  - 每题只从给定数重新计数，解数恰为 1 且与印刷答案全等
  - 难度带：Easy ≤44 / Medium ≤38 / Hard ≤34（实测 Easy 40、Medium 33–34、Hard 27–29，命中目标 40/34/28 附近）
  - Hard 的给定数严格少于 Easy
  - PDF 14 页、612×792pt（pypdf 实测）；同 seed 生成确定性
- 速度实测：6 题成书＋全部复检 0.8s——挖洞法是 Sudoku 的标准可收敛工艺，与本批 Kakuro 随机填充法形成对照（见批次 STATUS 的 R&D 记录）
