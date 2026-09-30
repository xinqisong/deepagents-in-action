# 能选择 Skill 的执行模式

用户能够将 Python 脚本映射到 sandbox scripts，将 TypeScript 辅助模块映射到 interpreter skills，并指出普通 `FilesystemBackend` 没有脚本执行能力。这说明用户已经区分了文件访问、沙箱执行和解释器导入三种能力。

## Evidence

用户正确回答了两种资源的执行方式及普通文件 Backend 的能力边界。

## Implications

可以进行本章综合设计验收：从目录结构、渐进式披露、namespace、权限策略到执行环境，完整设计一个可复用 Skill。
