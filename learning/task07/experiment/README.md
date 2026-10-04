# 实验区

实验按“一个变量一次引入”的顺序排列：

1. `01-checkpointer/`：只研究同一 `thread_id` 的短期状态；
2. `02-store/`：只研究跨 thread 数据和 namespace 隔离；
3. `03-composite-backend/`：把 Store 接到 Deep Agent 的文件工具，观察路径路由和 `memory=` 加载。
4. `04-memory-write/`：让 Agent 通过 `edit_file` 写入记忆，再用新 thread 读取。
5. `05-scopes/`：比较用户级、Agent 级和组织级 namespace。
6. `06-concurrency/`：观察同文件覆盖冲突和事件日志整合。

前两个实验不需要模型密钥。每次只修改一个变量，并把观察写进上一级的 [observations.md](observations.md)。

实验输出中的 ID、namespace 和文件 key 可以记录；真实密钥、完整 `.env`、数据库密码不能记录。
