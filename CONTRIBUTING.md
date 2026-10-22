# 更新指引

用于后续维护这个仓库。重点说明 **Power BI 报表文件（.pbix）做好后如何补进来**。

---

## 一、日常更新流程

```bash
cd taobao_sales_analysis

# 看改了哪些
git status
git diff

# 提交
git add -A
git commit -m "docs: 补充 xxx"
git push
```

提交信息建议用前缀标明类型，方便回溯：

| 前缀 | 用途 | 例子 |
| --- | --- | --- |
| `feat:` | 新增分析或图表 | `feat: 增加价格带结构图` |
| `fix:` | 修正口径或计算错误 | `fix: 人均消费分母排除已取消订单` |
| `docs:` | 文档 | `docs: 补充 Power BI 复现指南` |
| `data:` | 数据或结果表更新 | `data: 重跑 outputs` |
| `chore:` | 配置、依赖 | `chore: 增加 requirements.txt` |

---

## 二、Power BI 报表（.pbix）怎么补进去

### 先判断文件大小

`.pbix` 的大小取决于数据是**内嵌**还是**直连**：

| 连接方式 | .pbix 典型体积 | 建议 |
| --- | --- | --- |
| 导入模式（数据被打包进文件） | 10–80 MB | 可以直接提交；超过 50 MB 建议用 Git LFS |
| DirectQuery / 实时连接（只存结构） | 1–5 MB | 直接提交即可 |

查看方式：文件 → 选项和设置 → 选项 → 当前文件 → 数据加载，或直接看文件属性。

### 情况 A：文件小于 50 MB（最常见）

直接提交：

```bash
# 把 .pbix 放到 bi/ 目录下，命名建议用英文
cp ~/Desktop/淘宝消费看板.pbix bi/taobao-dashboard.pbix

git add bi/taobao-dashboard.pbix
git commit -m "feat: 提交 Power BI 看板源文件"
git push
```

同时改 README 的「看板」一节，在截图下面加一行：

```markdown
源文件：[`bi/taobao-dashboard.pbix`](bi/taobao-dashboard.pbix)（需要 Power BI Desktop 打开）
```

### 情况 B：文件超过 50 MB

用 Git LFS 管理（一次配置，之后透明处理）：

```bash
git lfs install
git lfs track "*.pbix"
git add .gitattributes
git commit -m "chore: 启用 Git LFS 管理 pbix"
```

之后正常 `git add` / `commit` / `push` 即可，LFS 会自动把大文件存到 LFS 服务。

> 注意：GitHub 免费账号的 LFS 额度是 1 GB 存储 / 1 GB 月流量，单个 `.pbix` 够用。若不想占额度，改用情况 C。

### 情况 C：不想把二进制放进仓库（推荐用于大文件）

把 `.pbix` 作为 **Release 附件**上传，仓库里只留链接：

1. 在 GitHub 仓库页 → 右侧 **Releases** → **Draft a new release**
2. Tag 填 `v1.0`，标题填「看板源文件」
3. 把 `.pbix` 拖进附件区 → **Publish release**
4. 复制附件链接，写进 README：

```markdown
源文件：[下载 taobao-dashboard.pbix](https://github.com/<你的用户名>/<仓库名>/releases/download/v1.0/taobao-dashboard.pbix)
```

这样仓库保持轻量，访问者仍能拿到完整文件。

### 同时要更新的三处

| 位置 | 改什么 |
| --- | --- |
| `README.md` 看板一节 | 加 `.pbix` 链接或下载链接 |
| `bi/p1.png` ~ `p4.png` | 用最终版截图**替换**旧图（同名覆盖，README 不用改） |
| `bi/taobao-midnight.json` | 若主题有调整，重新导出并覆盖 |

替换截图后提交：

```bash
git add bi/p1.png bi/p2.png bi/p3.png bi/p4.png
git commit -m "docs: 更新看板截图"
git push
```

> GitHub 有图片缓存，替换同名文件后页面可能仍显示旧图。强制刷新（Ctrl+Shift+R）或等几分钟即可。

---

## 三、不要提交的东西

`.gitignore` 已处理，这里说明原因：

| 不该提交 | 原因 |
| --- | --- |
| `项目介绍_简历版.md` | 求职材料，含自我评价与岗位适配分析，不适合公开 |
| `__pycache__/`、`.venv/` | 环境产物，体积大且与平台相关 |
| `*.pbix~`、`.pbixSettings/` | Power BI 编辑时的临时锁文件 |

### 凭据

目前仓库内没有硬编码密码。若以后把数据库连接写进代码，务必改为读环境变量：

```python
import os
pwd = os.environ.get("MYSQL_PWD")
```

并确保 `.env` 已被 `.gitignore` 忽略。**已经推到公开仓库的密码必须视为泄露，改密码后还要清理历史提交。**

---

## 四、提交前自检

- [ ] `git status` 里没有 `.venv/`、`__pycache__/`、个人材料
- [ ] 新增的 `.md` 里没有粘贴数据库密码、内网地址
- [ ] 图片路径用相对路径（`bi/p1.png`），不要用本机绝对路径
- [ ] 改了代码就重跑一次 `python src/main.py`，确认 `outputs/` 结果与 README 中的数字一致
