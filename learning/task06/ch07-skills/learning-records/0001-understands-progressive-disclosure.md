# 理解 Skills 的渐进式披露与 Tool 边界

用户能够解释：把所有 Skill 正文放进系统提示词会造成上下文膨胀；Agent 应先根据 `name` / `description` 判断相关性，再读取 `SKILL.md` 正文，必要时继续读取脚本等辅助资源。用户也能区分“调用 GitHub API 获取 PR diff”这一原子能力和“按 diff、测试、模板完成 PR 审查”这一规范化工作流：前者是 Tool，后者适合封装为 Skill。后续需要进一步澄清：Skill 通常编排或指导 Tool，脚本能否执行还取决于 Backend、解释器或沙箱。

## Evidence

用户用自己的话回答了第一课的三道回忆题，并主动指出 Skills 更适合规定性、规范性流程。

## Implications

可以跳过 Skill / Tool / Memory 的基础区分，进入 `SKILL.md` 的最小目录结构、frontmatter 和 `description` 路由实验。
