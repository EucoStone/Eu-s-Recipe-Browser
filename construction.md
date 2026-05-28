mc-recipe-calculator/          # 项目根目录
├── backend/                   # 后端服务
│   ├── app/                   # 应用核心代码
│   │   ├── api/               # API 路由层
│   │   │   ├── v1/            # API 版本 v1
│   │   │   │   └── endpoints/ # 存放各功能模块的路由文件
│   │   │   └── deps.py        # 依赖注入（如数据库连接）
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 读取 .env 的配置类
│   │   │   └── database.py    # MongoDB 连接管理
│   │   ├── models/            # MongoDB 文档模型（使用 Beanie/ODMantic）
│   │   ├── schemas/           # Pydantic 模式（请求/响应数据校验）
│   │   ├── services/          # 业务逻辑层（核心计算逻辑）
│   │   ├── utils/             # 工具函数（如解析 JSON）
│   │   └── main.py            # FastAPI 应用入口
│   ├── uploads/               # 临时存放用户上传的文件
│   ├── .env                   # 环境变量（不要提交到 Git）
│   └── requirements.txt       # Python 依赖清单
├── frontend/                  # 前端项目（Vite + Vue 3）
│   ├── src/
│   │   ├── api/               # 封装和后端交互的 API 请求
│   │   ├── assets/            # 静态资源
│   │   ├── components/        # 可复用的 Vue 组件
│   │   ├── router/            # 前端路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── views/             # 页面级组件
│   │   ├── App.vue
│   │   └── main.ts
│   └── package.json
└── docker-compose.yml         # （可选）用于一键启动所有服务