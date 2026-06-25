# Python 版 — 多Agent临床辅助决策系统

基于 **LangGraph + FastAPI + GraphRAG + PostgreSQL** 构建。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 DeepSeek API Key

# 3. 启动服务
uvicorn src.api.main:app --reload --port 8000

# 4. 打开 Swagger 文档
# http://localhost:8000/docs
```

## Docker 启动

```bash
docker-compose up -d
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/clinical/analyze` | 运行完整5-Agent Pipeline |
| POST | `/api/v1/clinical/icd10/search` | 搜索ICD-10编码 |
| GET  | `/api/v1/clinical/icd10/{code}` | 查询特定ICD-10编码 |
| POST | `/api/v1/clinical/ddi/check` | 药物交互检查 |
| GET  | `/health` | 健康检查 |

## 运行测试

```bash
pytest tests/ -v
```

## Vue Frontend Workbench

The Python implementation includes a Vue 3 demo workbench in `frontend/`.

```bash
# Backend
uvicorn src.api.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` and `/health` to
`http://localhost:8000`.

Frontend environment:

```bash
VITE_API_BASE_URL=/api/v1
```

Streaming analysis endpoint:

```http
POST /api/v1/clinical/analyze/stream
Content-Type: application/json
Accept: text/event-stream
```

Request body:

```json
{
  "patient_description": "Patient narrative...",
  "thread_id": "demo-001"
}
```

Each Server-Sent Event uses this data payload:

```json
{
  "thread_id": "demo-001",
  "stage": "intake",
  "status": "completed",
  "payload": {},
  "errors": []
}
```

Valid stages are `intake`, `diagnosis`, `treatment`, `coding`, `audit`,
`done`, and `error`.
