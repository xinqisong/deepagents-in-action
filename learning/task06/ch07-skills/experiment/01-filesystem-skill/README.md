# Experiment 01：FilesystemBackend 加载 Skill

本实验只验证 Skill 的发现和按需读取，不验证生产权限和脚本执行。

## 运行

```bash
cd learning/task06/ch07-skills/experiment/01-filesystem-skill
../../../.venv/bin/python run_demo.py
```

脚本会优先读取 `learning/task06/ch07-skills/.env`，如果不存在则尝试复用 `learning/task06/.env`。真实 `.env` 不要提交。

## 观察点

1. `skills=["/skills/"]` 指向父目录；
2. Agent 先根据 `name` / `description` 判断是否相关；
3. 相关任务才读取 `SKILL.md` 正文；
4. 安全变更才需要读取 `references/security-checklist.md`；
5. 只有提供执行能力的 Backend 才能真正运行 `scripts/` 中的代码。
