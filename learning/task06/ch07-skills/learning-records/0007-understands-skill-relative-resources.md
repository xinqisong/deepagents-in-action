# 理解 Skill 辅助资源的相对路径

用户能够判断 `pr-review` 的 `assets/`、`references/` 和 `scripts/` 应放在该 Skill 目录下，而不是 Backend 根目录。用户也理解了第一次实验为什么会读到根目录资源：Agent 根据 `SKILL.md` 中的相对引用寻找文件，而错误放置的根目录文件恰好被找到。

## Evidence

用户回答应将资源放在 `PR review` Skill 目录下的 `assets`、`references` 和 `scripts` 中。

## Implications

可以比较修正前后的实际读取路径，并进一步观察“读取脚本”和“执行脚本”的区别。
