# 能选择组织级与用户级 namespace 边界

用户能够判断共享 Skill 应绑定组织的统一标识，个人 Skill 应绑定用户标识；如果个人 Skill 错误使用组织 ID，就会让个人内容进入组织共享空间，造成发现范围扩大和隐私泄露。

## Evidence

用户用团队共享 ID、用户本人绑定和个人 Skill 泄露到组织三个层面解释了 namespace 边界。

## Implications

可以开始 `CompositeBackend` + `StoreBackend` 的最小隔离实验，验证路径路由和 namespace 不是同一层概念。
