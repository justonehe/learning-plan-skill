# Learning Plan Skill

一个给 agent 使用的自学陪伴 skill。**前提:学习者具有自主性**——学习的主导权、进度责任、结果责任都在学习者。它**不是学习管理工具**(不督学、不提醒、不打卡、不对学习结果负责),也**不是学习评测工具**(一切检测都是形成性的,只产生"下一步学什么"的信号;学习者不应根据它的反馈判断自己的学术水平)。它做的事:摸底、生成学习计划、跨源整合资料(公开课/教材/论文/视频)、设计检查点,并在学习中担任基于资料的答疑者;全程用 Markdown 记录、Git 追踪。

明确不做的功能:进度百分比、打卡天数、徽章、掌握度仪表盘、学习时长统计、对人的等级评定、与他人比较。

## 目录内容

```text
learning-plan-skill/
  SKILL.md                        # 给 agent 的核心行为规范(~300 行)
  references/
    labs-and-checkpoints.md       # 检查点:课程 lab 采用纪律、评测机规范、自查清单
    multimodal-video.md           # 视频多模态:原件优先、成本三档、消化流程
    coursepack-synthesis.md       # 公开课资料包与多源整合:版本配套、衔接与记号
  scripts/
    learning_skill.py             # 零依赖 CLI(init/session/lab/video/course/synthesis/resource/audit/entry/status/commit)
    smoke_test.py                 # 快速自测
  templates/                      # 由脚本渲染的文件模板(不进入 agent 上下文)
```

## 学习模式(两种)

判定标准只有一个:学习产出能否被程序或资料客观核对?学科名只是示例,不是判据。

```text
strong  强核对:产出可被程序或资料客观检验(编程/工程/可逐步核对的推导等)。检查点是可机判的 lab。
qa      轻监督答疑:产出无法客观检验(哲学/文学/历史等)。检查点是自查清单。
auto    由 agent 按可评测性判据判断,可按阶段混合。
```

"强"指核对工具的严格性,不指强制性:两种模式下检查点都是邀约(交付—提交—检查),学习者决定做不做、何时提交;未提交而转段提醒一次后尊重并记录。学习期 agent 一律保持克制:等学习者开口——提问就答疑,陈述理解就对照资料原意核对,提交检查点才检查。

## 三层所有权

```text
mission.md   属于用户:学习任务的契约(边界/目标判据/预算/模式),agent 只起草记录
plan.md      agent 起草,用户守门:确认后才执行;用户大改致不可达 mission 时,agent 有异议义务(一次,留痕)
resources.md agent 拍板,但每条必须写入选理由——这是用户挑战 agent 选择的接口
```

## 快速开始

```bash
# 建仓
python scripts/learning_skill.py init ~/learning/rl-study \
  --topic "强化学习" --goal "理解 RL 在大模型训练中的作用,并能复现一个小实验" --mode auto

# 每次学习会话
python scripts/learning_skill.py session ~/learning/rl-study --title "第一次诊断"

# 强核对模式:自建 lab(评测机先写后做)
python scripts/learning_skill.py lab ~/learning/rl-study --name "tiny-ppo"

# 视频建档与抽帧(幻灯片课用 --mode scene,板书课用默认 interval)
python scripts/learning_skill.py video ~/learning/rl-study \
  --title "PPO 讲解" --source /path/to/video.mp4 --transcript /path/to/t.md --mode scene

# 公开课资料包 / 多源整合工作区
python scripts/learning_skill.py course ~/learning/rl-study --title "CS285" --source "<官网>"
python scripts/learning_skill.py synthesis ~/learning/rl-study

# 可选:生成学习者入口页(纯链接聚合,派生快照,无进度元素)
python scripts/learning_skill.py entry ~/learning/rl-study

# 批量资料拉取后的目录审计（完成报告前必须通过）
python scripts/learning_skill.py audit ~/learning/rl-study

# 状态与提交
python scripts/learning_skill.py status ~/learning/rl-study
python scripts/learning_skill.py commit ~/learning/rl-study --message "state: update progress"
```

## agent 的使用方式

每次会话开始,读:mission.md、state.md、plan.md、profile.md、resources.md、最近一次 dialogue/*.md(不通读 raw/)。
每次会话结束,更新:raw/ 原始对话、dialogue/ 整理版、state.md 及相关文件,然后 commit。

完整行为规范见 SKILL.md;检查点、视频、多源整合的细则在 references/ 下,按需加载。

## 资料入口约定

```text
labs/        实际作业仓库、handout、starter、tests
videos/      主线/辅助播放列表的逐集介绍、阶段映射和字幕
readings/    精选论文/教材文件与索引
coursepacks/ 课程版本、schedule 和官方 lecture/slides 静态原件
```

这些入口保持唯一。不得把作业和视频先藏进 `coursepacks/` 再通过软链接暴露;播放列表只有字幕而没有逐集介绍也不算建档完成。

## 依赖

Python ≥ 3.9;git 可选(无 git 时降级为纯 Markdown 记录);ffmpeg 可选(仅抽关键帧需要)。
