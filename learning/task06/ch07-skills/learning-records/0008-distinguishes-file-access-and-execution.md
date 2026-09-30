# 区分 Skill 文件访问与脚本执行能力

用户能够根据读取路径确认 Skill 辅助资源已从 `skills/pr-review/` 正确加载，并解释 `FilesystemBackend` 不具备脚本执行能力。用户还联想到需要提供 `execute` 能力的沙箱 Backend；后续需要进一步区分文件访问权限、执行环境和写入权限三条安全边界。

## Evidence

用户用自己的话说明了读取路径、当前 Backend 的能力限制，并指出具备执行能力的 execute/sandbox 后端方向。

## Implications

可以进入 Skills 的权限和沙箱讨论，不必重新讲文件路径或渐进式披露。
