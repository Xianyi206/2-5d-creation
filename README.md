# 2.5D 创作 Skill

以分层平面素材、视差和角色运动构建具有景深的 2.5D 网页场景。让 AI 在制作游戏活动页、版本专题页和 H5 开屏时，先判断素材能做到什么，再安排角色运动、分层景深、粒子与转场。

这是一套可下载的 Skill 指令、参考文档和辅助脚本。它不是现成网页模板，也不附带角色原画、Spine 模型或运行库。

## 可以用来做什么

- 分析参考画面的层级、入场节奏、待机循环和交互响应。
- 根据现有素材选择 Spine、分层图片或单张立绘的实现路径。
- 组织背景、光雾、远近粒子、角色、前景和界面之间的运动关系。
- 处理桌面与移动端构图、暂停动效、减少动态效果和加载失败回退。
- 按实际浏览器画面、运行表现和构建结果验收。

## 使用

[下载 Skill 压缩包](https://github.com/Xianyi206/2-5d-creation/releases/download/public-2026-09-09/2-5d-creation.zip) · [查看发布页](https://github.com/Xianyi206/2-5d-creation/releases/tag/public-2026-09-09)

压缩包解压后得到完整的 `2-5d-creation` 文件夹。若下载整个仓库，则使用下面的目录：

下载仓库后，将 `skills/2-5d-creation` 整个文件夹放入所用 AI 工具支持的 Skills 目录。保留 `references`、`scripts` 和 `agents` 子目录。

在能按名称调用 Skill 的工具中，可以这样描述任务：

> 使用 $2-5d-creation，为我制作一个原创幻想风格的游戏活动开屏。我会提供角色素材，请先判断适合采用哪种动画方式，再实现桌面和移动端效果。

也可以让 AI 从 [SKILL.md](skills/2-5d-creation/SKILL.md) 开始读取，并按任务需要打开其中链接的参考文档。实际网页仍需要单独的项目环境和有权使用的素材。

## 素材决定实现路径

| 输入 | 适合的处理 |
| --- | --- |
| Spine 骨骼与图集 | 检查导出版本、动画和约束，再接入匹配的运行库 |
| 分层 PSD / PNG | 以独立部件、枢轴或网格组织运动 |
| 单张透明立绘 | 使用克制的整体运动和场景景深，明确局部动画的上限 |

单图自动拆分、补全和绑定仍属于实验路径，尚未完成端到端验证。已有 Spine 动画的播放能力与自动生成骨骼是两回事。

## 文件导航

| 文件 | 内容 |
| --- | --- |
| [SKILL.md](skills/2-5d-creation/SKILL.md) | 任务入口与素材分流 |
| [motion-system.md](skills/2-5d-creation/references/motion-system.md) | 运动层级、幅度、相位与响应式构图 |
| [spine-pipeline.md](skills/2-5d-creation/references/spine-pipeline.md) | Spine 检查和集成要点 |
| [single-image-pipeline.md](skills/2-5d-creation/references/single-image-pipeline.md) | 实验性单图处理路线与验证边界 |
| [acceptance.md](skills/2-5d-creation/references/acceptance.md) | 浏览器、视觉和运行验收 |

## 辅助脚本

`inspect_spine_json.mjs` 只读取给定的骨骼 JSON，汇总版本、边界、骨骼、附件、约束和动画信息。需要 Node.js：

```text
node skills/2-5d-creation/scripts/inspect_spine_json.mjs <skeleton.json>
```

`seethrough_remote.py` 是面向官方示例的实验性远程适配器，使用 Python 标准库。`probe` 和 `run-sample` 会访问外部服务，运行前请阅读对应参考文档；它不会自动提交本机角色图片。`poll` 只读取指定输出目录中的本地回执。

运行已有的适配器回归测试：

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

这些测试使用合成响应，不访问在线推理服务，也不证明单图生成动画已经可用。

## 发布范围

仓库仅包含 Skill、辅助脚本和合成响应测试。不包含第三方角色素材、模型权重、账户凭据或真实运行记录。使用者需要为自己的素材和所选运行库分别确认使用与分发条件。

本次公开尚未另行指定开源许可证。
