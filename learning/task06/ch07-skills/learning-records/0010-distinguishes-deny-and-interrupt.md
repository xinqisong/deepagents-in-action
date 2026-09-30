# 能区分共享 Skill 与个人 Skill 的写入策略

用户能够选择：共享 Skill 的写入使用 `deny`，个人 Skill 的写入使用 `interrupt`，并解释这是公共资产治理与个人可定制性之间的差异。下一步需要把策略具体化为路径、操作和 Backend 路由，而不是只停留在模式名称。

## Evidence

用户明确回答共享 Skill 应禁止修改，个人 Skill 可以暂停后人工确认，并给出了治理理由。

## Implications

可以进入共享/个人 Skill 分层、`CompositeBackend` 路由和路径权限矩阵实验。
