# 实验 5：作用域与 namespace 设计

这个实验不调用模型，只观察相同 key 在不同 namespace 下的可见性。

运行：

    cd learning/task07
    uv run python experiment/05-scopes/namespace_scope_demo.py

重点观察：

- user-scoped：user-a 和 user-b 的偏好互相不可见；
- agent-scoped：不同用户读取同一个 Agent namespace 时看到同一份知识；
- organization-scoped：组织策略可以被多个用户读取；
- namespace 只负责数据分区，不自动提供只读权限。

最后一点很重要：如果组织策略不允许 Agent 修改，还需要应用层写入约束、权限规则或人工审批。
