# 公开课资料包与多源整合

整合公开课、教材、论文等多源资料前必读。总规则见 SKILL.md §6;本文件是操作细则。

## 1. 资料包的处理顺序

某主题存在高质量公开课,且课程同时提供视频、幻灯片、讲义、Lab、作业或阅读清单时,按结构化资料包处理:

```text
1. 课程官网 / syllabus / schedule:确定课程结构、章节顺序、先修要求
2. 官方讲义 / 幻灯片:课程内概念的主要依据
3. Lab / assignment:可操作任务来源(采用纪律见 references/labs-and-checkpoints.md)
4. 视频 + 关键帧:补讲解过程、板书、演示(见 references/multimodal-video.md)
5. 字幕 / transcript:用于检索与定位,不单独作为公式图表依据
6. reading list:追溯教材与论文
```

## 2. 同源配套对版本

从同一门课取多种件(讲义 + 视频 + lab)时,核对为**同一学期版本**——跨年混用会对不上页码、编号与作业接口。版本记录在 coursepack README 的 Term / version 字段(必填)。

幻灯片明显过时、有笔误、或视频中有明确修正时,记录修正理由;版本与内容差异写入 synthesis/conflicts.md,保留差异并标注来源,不强行合并。

## 3. 不把 skill 降级为公开课处理器

不要把学习计划变成"学完某一门公开课"。公开课只是资料来源之一:

```text
公开课:提供结构、讲解、Lab、作业和学习路径
教材:提供稳定、系统、可查证的基础解释
论文:提供原始方法、前沿进展、关键实验和争议点
官方文档:提供实现细节、API、工程约束
项目仓库:提供可运行代码、复现实验、工程样例
博客 / 讲义:提供补充解释,不作为唯一依据
视频:提供讲解过程、视觉材料和操作演示
```

最终计划是目标驱动的组合方案,不是资料清单。里程碑骨架由 mission 的目标判据决定;现成 syllabus 的价值在于参考概念顺序与依赖关系,仅当某门课与目标高度重合时,整课采用才作为捷径成立。

## 4. 目标驱动抽取

不要求用户完整学完任何一份资料。抽取粒度:

```text
课程中的某几讲 / 幻灯片中的某几页 / 教材中的某几节
论文中的方法、实验或相关工作部分 / Lab 中的某个任务
视频中的某个时间段 / 项目仓库中的某个模块 / 官方文档中的某个 API
```

每个阶段要回答:这个阶段解决什么目标?哪个资料作主线?哪些只用于补洞?哪些跳过?哪些以后再看?

拼接处做两个检查:

- **衔接**:选段交界处确认前置概念已被此前阶段覆盖;有缺口就补一小段资料,或在 plan 中注明。
- **记号**:不同资料对同一概念的符号、术语不一致时,记入 synthesis/conflicts.md;学习期答疑按用户正在读的那份资料的记号作答。

## 5. 多源综合文件

资料来源超过一个时,建立 synthesis 工作区(`python scripts/learning_skill.py synthesis <repo>`):

```text
source-map.md      候选资料、类型、可信度、适用范围
objective-map.md   目标拆成知识点 / 能力点,映射到具体资料片段
conflicts.md       资料间冲突、版本差异、术语与记号差异
selected-path.md   最终路径,以及为什么选这些片段
```

selected-path 的"为什么选"与 resources.md 的入选理由是 agent 拍板的可查验接口,不可省略。

## 6. 组合约束

每阶段一个主线资料(保持学习顺序稳定),补充不超过 2 份且只解决明确问题,不扩展成新的完整路线。多门好课并存时:一门作阶段主线,其余只抽更强的部分,例如:

```text
A 课的第 2-4 讲作为概念主线
B 课的某个 Lab 作为操作任务
教材第 3 章用于补基础定义
论文第 4 节用于理解原始方法
```

## 7. 课程建档

对采用的公开课建立独立目录(`python scripts/learning_skill.py course <repo> --title ... --source ...`):

```text
coursepacks/<course>/
  README.md           课程身份(含 Term/version)、可得材料、先修、阅读、使用policy
  schedule.md         课程结构映射表(讲次 / 幻灯片 / 视频 / lab / 是否采用)
  extracted-parts.md  只记录本计划实际采用的部分
  notes.md            备注
  materials/          官方 lecture source、slides、讲义等同学期静态原件
  assets/             coursepack 自身需要的图像等资产
```

实际学习入口保持唯一：作业仓库放根级 `labs/`，视频逐集记录放根级 `videos/`，论文/教材文件放根级 `readings/`。`schedule.md` 可以链接它们，但不得在 coursepack 内复制或另建 `labs/assignments/videos/readings/supplements`。外部作业若用 Git submodule，直接建在 `labs/<assignment>`，不要先放进 coursepack 再用软链接暴露。
