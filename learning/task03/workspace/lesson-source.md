# Task 03 实验资料

虚拟文件系统的核心价值是把资料和中间结果放到模型上下文之外，需要时再读取。

Backend 决定文件的存储位置和生命周期：StateBackend 适合临时状态，FilesystemBackend 适合本地工作区，StoreBackend 适合跨会话持久化。

context engineering 关注的不只是上下文窗口大小，还包括信息如何保存、检索、压缩和按需注入。

TODO：完成 Task 03 的文件系统实验，并记录安全边界。
