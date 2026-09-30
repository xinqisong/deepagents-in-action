# 理解 Skills 源路径指向父目录

用户能够判断 `skills=` 应指向包含多个 Skill 子目录的 `skills/` 父目录，而不是直接指向某个 `SKILL.md` 文件。这个判断建立在“框架扫描父目录、从子目录发现 Skill 元数据”的理解上。

## Evidence

用户直接回答“应该指向 Skills 目录”。

## Implications

可以开始最小 `FilesystemBackend` 实验，重点观察文件树、元数据发现和正文按需读取，而不是继续停留在路径概念。
