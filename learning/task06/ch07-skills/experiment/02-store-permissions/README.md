# Experiment 02：Store namespace 与路径权限

本实验观察三件事：

1. `/skills/shared/` 和 `/skills/personal/` 是否进入不同 namespace；
2. 共享 Skill 写入是否被 `deny` 拒绝；
3. 个人 Skill 和 `/reports/` 写入是否触发人工审批中断。

先阅读 `demo.py`，预测行为，再运行：

```bash
cd learning/task06/ch07-skills/experiment/02-store-permissions
../../../.venv/bin/python demo.py
```

真实 `.env` 不要提交。实验需要当前本地模型配置和一个 checkpointer，因为 `interrupt` 必须保存暂停状态。
