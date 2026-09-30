# 理解 namespace 的数据隔离作用

用户能够解释 namespace 用于隔离数据，并指出共用 namespace 会造成个人 Skill 被其他用户发现、同名 Skill 覆盖、报告相互污染和私有内容泄露。这个理解把“权限模式”与“存储隔离”区分开了。

## Evidence

用户用自己的话完整描述了共用 namespace 的四类风险。

## Implications

可以进入运行时 namespace 构造和 `CompositeBackend` 路由实验，重点检查组织级共享库与用户级个人库的隔离。
