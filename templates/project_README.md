# {{topic}}

- Topic: {{topic}}
- Goal: {{goal}}
- Mode: {{mode}}
- Created: {{created}}

## How to use

每次学习会话开始时,agent 先读:

```text
mission.md  state.md  plan.md  profile.md  resources.md  最近一次 dialogue/*.md
```

会话结束时更新 Markdown 记录并提交 git。

学习者入口:资料链接集中在 resources.md(按阶段标注);
也可以运行 `python scripts/learning_skill.py entry <repo>` 生成 index.html 链接聚合页(可选,派生快照)。

资料入口保持唯一:`labs/` 放作业,`videos/` 放逐集介绍与字幕,`readings/` 放论文/教材,`coursepacks/` 只放课程映射和官方 lecture 静态原件。批量拉取后运行 `python scripts/learning_skill.py audit <repo>`。
