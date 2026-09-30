---
name: pr-review
description: 审查代码变更，检查 diff、测试和项目规范，并输出带证据的问题与建议。用户要求审查 PR 或代码变更时使用。
---

# pr-review

## Workflow

1. 读取并总结当前 diff，确认变更范围。
2. 检查相关测试、测试结果和项目规范。
3. 如果变更涉及认证、授权、密钥、用户数据或外部输入，读取 `references/security-checklist.md`。
4. 汇总前使用 `assets/report-template.md` 组织报告；如果需要统计变更行数，尝试使用 `scripts/count_changed_lines.py`。
5. 对每个问题输出位置、严重程度、证据和修复建议；如果没有发现问题，明确说明检查范围。

## Execution boundary

脚本是否能够运行取决于当前 Backend 是否提供安全的执行能力。不能执行时，不要声称已经运行；可以读取脚本并说明需要什么运行环境。
