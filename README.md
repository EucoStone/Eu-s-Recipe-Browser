# RecipeBrowser

RecipeBrowser 是一个面向 Minecraft `KubeJS export` 配方导出的浏览与材料计算工具。

它支持：

- 导入 `kubejs/export/recipes` 目录下的配方 JSON
- 从模组或资源包中导入 `zh_cn.json`
- 按物品 ID、英文名或中文名搜索配方
- 递归展开合成树并计算基础材料

## 技术栈

- 后端：FastAPI
- 前端：Vue 3 + Vite + Pinia
- 数据库：MongoDB

## 项目结构

- `backend/`：FastAPI 后端
- `frontend/`：Vue 前端
- `script/extract.py`：从模组文件中提取 `zh_cn.json`
- `docker-compose.yml`：一键启动 MongoDB、后端、前端

## 快速启动

### 方式一：Docker Compose

前提：已安装并启动 Docker Desktop。

在项目根目录执行：

```bash
docker compose up --build
```

访问地址：

- 前端：`http://localhost:3000`
- 后端文档：`http://localhost:8000/docs`

### 方式二：本地分别运行

#### 1. 启动 MongoDB

默认连接地址：

```text
mongodb://localhost:27017
```

#### 2. 启动后端

```bash
cd backend
copy .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问地址：

- 前端：`http://localhost:3000`
- 后端文档：`http://localhost:8000/docs`

## 导入配方

在前端选择 `local/kubejs/export/recipes` 目录，或者一次选择多个 JSON 文件进行导入。

常见情况：

- `/kubejs export`：生成按 mod 和类别分层的配方目录
- `/kubejs export recipes`：与前者不同，可能不是本工具当前最适合的输入

## 导入中文名称

RecipeBrowser 支持导入 `zh_cn.json`，用于显示中文名称并支持中文搜索。

### 常见位置

- `mods/<mod>.jar` 内部：
  - `assets/<modid>/lang/zh_cn.json`
- `resourcepacks/<pack>.zip` 内部：
  - `assets/<modid>/lang/zh_cn.json`

### 前端操作

1. 点击“导入中文名称”区域
2. 选择一个或多个 `zh_cn.json`
3. 上传后，搜索和合成树会优先显示中文名称

### 中文搜索

上传 `zh_cn.json` 后，可以直接搜索：

- `样板供应器`
- `逻辑处理器`
- `导线`

如果某个物品存在对应翻译键，系统会优先显示中文名，否则回退为规则化英文名。

## `script/extract.py`

这个脚本用于批量提取整合包中的 `zh_cn.json`，适合在你想要整理模组汉化文件时使用。

### 用法

把脚本放在整合包的 `mods` 文件夹同级或整合包根目录下，然后运行：

```bash
python script/extract.py --root "D:\\path\\to\\your\\instance"
```

默认会在根目录下创建：

```text
zh_cn/
```

提取结果会按模组名分目录保存：

```text
zh_cn/ae2/xxx.json
zh_cn/minecraft/xxx.json
```

### 说明

- 脚本会递归扫描根目录下的 `.jar` 和 `.zip`
- 只提取 `assets/*/lang/zh_cn.json`
- 同一来源文件会被保存为单独文件，避免覆盖

## API

- `POST /api/v1/upload`
- `GET /api/v1/recipes/search?query=xxx`
- `POST /api/v1/calculate`
- `GET /api/v1/health`

## 主要功能

- JSON 配方导入
- MongoDB 配方索引存储
- 物品模糊搜索
- 合成树递归计算
- 基础材料总表
- 中文语言文件导入

## 后续可继续增强的方向

- 更完整的 Minecraft 本地化键解析
- 标签 `tag` 的中文映射
- 更强的循环配方识别和提示
- 更细粒度的导入任务进度展示

