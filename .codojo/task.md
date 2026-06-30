# 学习计划

> 根据你的能力评估自动生成。目标是先理解项目完整流程，再能面向面试讲清架构、关键取舍和代码实现。

## 学习概要

- **总知识点数**：25 个
- **预计学时**：约 28-36 小时
- **学习路径**：项目全景 -> Python 分层结构 -> 数据模型 -> API 入口 -> LangGraph Pipeline -> 五个 Agent -> GraphRAG 与医疗标准 -> 前端工作台 -> 部署与测试 -> 面试表达
- **重点补强**：LLM 应用开发、Agent 设计、GraphRAG/Neo4j、FastAPI/Pydantic、测试
- **快速带过**：医疗术语已有基础，但仍会结合项目代码巩固 ICD-10、FHIR、DDI、HIPAA 的工程用途

## 模块 0：项目全景

### 0.1 项目全景：分层结构与模块关系
- **类型**：纯理论（无实践任务）
- **难度**：一星
- **前置知识**：无
- **学习目标**：建立项目整体认知，知道项目分了哪些层、每层负责什么、为什么这样分
- **理论要点**：根目录、后端 `src/`、前端 `frontend/`、文档 `docs/`、测试 `tests/`、基础设施配置之间的关系；API 层、Agent Pipeline 层、服务层、模型层的职责边界
- **涉及文件**：`README-python.md`、`docs/00-项目概览.md`、`src/`、`frontend/src/`

## 模块 1：Python 后端基础骨架

### 1.1 Python 包结构与分层职责
- **类型**：理论 + 实践
- **难度**：一星
- **前置知识**：0.1
- **学习目标**：理解 `src/api`、`src/graph`、`src/agents`、`src/services`、`src/models` 的分工
- **理论要点**：包导入、模块边界、单向依赖、为什么 Agent 不直接写 API 或数据库
- **实践任务**：画出从 `src.api.main:app` 到 `clinical_pipeline` 的调用链
- **涉及文件**：`src/api/main.py`、`src/api/routes.py`、`src/graph/clinical_pipeline.py`

### 1.2 Pydantic 数据模型与状态对象
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：1.1
- **学习目标**：理解请求模型、领域模型、共享状态如何约束数据结构
- **理论要点**：`BaseModel`、`Field`、可选字段、`model_dump`、嵌套模型、校验失败的意义
- **实践任务**：追踪 `AnalyzeRequest`、`ClinicalState`、`PatientInfo` 在一次分析请求中的作用
- **涉及文件**：`src/api/routes.py`、`src/graph/state.py`、`src/models/patient.py`、`src/models/diagnosis.py`、`src/models/treatment.py`

### 1.3 配置管理与外部依赖
- **类型**：理论 + 实践
- **难度**：一星
- **前置知识**：1.1
- **学习目标**：理解 `.env`、settings、LLM/Neo4j/PostgreSQL/Redis 配置如何进入代码
- **理论要点**：环境变量、默认值、开发配置和生产配置的区别
- **实践任务**：列出本项目运行需要的关键环境变量及其用途
- **涉及文件**：`.env.example`、`src/config/settings.py`、`docker-compose.yml`

## 模块 2：FastAPI API 入口

### 2.1 FastAPI 应用启动与路由注册
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：1.1、1.2
- **学习目标**：理解后端服务如何从 `uvicorn` 启动并暴露 HTTP 接口
- **理论要点**：`FastAPI()`、router、prefix、CORS、health check、Swagger
- **实践任务**：定位 `/health`、`/api/v1/clinical/analyze`、`/api/v1/clinical/icd10/search` 的实现
- **涉及文件**：`src/api/main.py`、`src/api/routes.py`

### 2.2 同步接口与流式 SSE 接口
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：2.1
- **学习目标**：理解普通分析接口和流式分析接口的区别
- **理论要点**：`StreamingResponse`、SSE 格式、`pipeline.invoke` 与 `pipeline.stream`、前端进度展示需要的事件协议
- **实践任务**：解释 `iter_analyze_events` 如何把 LangGraph chunk 转成前端事件
- **涉及文件**：`src/api/routes.py`、`frontend/src/api/clinicalApi.ts`

## 模块 3：LangGraph Pipeline 主线

### 3.1 ClinicalState：五个 Agent 的共享黑板
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：1.2
- **学习目标**：理解每个 Agent 读写哪些字段，数据如何在流水线中流转
- **理论要点**：共享状态、字段所有权、`errors` 累积、`current_agent`、`messages` reducer
- **实践任务**：做一张字段读写表：Intake、Diagnosis、Treatment、Coding、Audit 各自读写什么
- **涉及文件**：`src/graph/state.py`、`docs/02-架构设计详解.md`

### 3.2 StateGraph 节点、边与条件路由
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：3.1
- **学习目标**：理解 LangGraph 如何把五个 Agent 编排成可执行图
- **理论要点**：`StateGraph`、`add_node`、`add_edge`、`add_conditional_edges`、`END`、`MemorySaver`
- **实践任务**：手动解释 `intake -> diagnosis -> treatment -> coding -> audit` 的执行顺序
- **涉及文件**：`src/graph/clinical_pipeline.py`

### 3.3 Diagnosis 回环与防无限循环
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：3.2
- **学习目标**：理解为什么 Diagnosis 可以回到 Intake，以及如何限制重试次数
- **理论要点**：`needs_more_info`、`diagnosis_retry_count`、`MAX_DIAGNOSIS_RETRIES`、条件路由的工程意义
- **实践任务**：用一段话解释“信息不足时为什么不是直接失败”
- **涉及文件**：`src/graph/clinical_pipeline.py`、`src/agents/diagnosis_agent.py`

## 模块 4：LLM Agent 设计

### 4.1 Agent 的统一结构
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：3.1
- **学习目标**：理解 LLM Agent 的三段式结构：读 state、调用 LLM/服务、写回 state
- **理论要点**：system prompt、HumanMessage、`ChatOpenAI`、JSON 解析、异常兜底
- **实践任务**：对比 Intake、Diagnosis、Treatment、Coding 的函数结构，找出共性
- **涉及文件**：`src/agents/intake_agent.py`、`src/agents/diagnosis_agent.py`、`src/agents/treatment_agent.py`、`src/agents/coding_agent.py`

### 4.2 Intake Agent：自然语言到结构化患者信息
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：4.1
- **学习目标**：理解如何把患者叙述解析成结构化 JSON
- **理论要点**：prompt schema、字段默认值、LLM 输出清洗、Pydantic 二次校验
- **实践任务**：用示例患者文本手动标注会被提取到哪些字段
- **涉及文件**：`src/agents/intake_agent.py`、`src/models/patient.py`

### 4.3 Diagnosis Agent：诊断推理与 GraphRAG 候选
- **类型**：理论 + 实践
- **难度**：三星
- **前置知识**：4.1、3.3
- **学习目标**：理解诊断 Agent 如何结合患者信息、候选疾病、置信度和补充信息判断
- **理论要点**：鉴别诊断、证据链、recommended_tests、GraphRAG candidates、`needs_more_info`
- **实践任务**：解释肺炎示例为什么能从 fever/cough/chest pain 推出候选诊断
- **涉及文件**：`src/agents/diagnosis_agent.py`、`src/services/graphrag_service.py`

### 4.4 Treatment Agent：治疗方案与 DDI 检查
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：4.1
- **学习目标**：理解治疗建议为什么必须结合诊断、过敏史、当前用药
- **理论要点**：药物推荐、非药物治疗、随访计划、DDI 严重等级
- **实践任务**：追踪一个药物相互作用检查从 Agent 到 service 的路径
- **涉及文件**：`src/agents/treatment_agent.py`、`src/services/drug_interaction.py`

### 4.5 Coding Agent：ICD-10 与 DRG 输出
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：4.1
- **学习目标**：理解诊断结果如何映射为 ICD-10 编码和 DRG 分组
- **理论要点**：主诊断、次诊断、编码置信度、DRG 权重和平均住院日
- **实践任务**：查找 `J18` 类编码和 DRG 分组逻辑
- **涉及文件**：`src/agents/coding_agent.py`、`src/services/icd10_service.py`、`data/icd10cm/icd10cm_codes_2026.json`

### 4.6 Audit Agent：为什么合规审计不用 LLM
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：4.1
- **学习目标**：理解规则引擎在合规场景中的价值
- **理论要点**：HIPAA PHI、正则检测、脱敏、audit trail、确定性和可审计性
- **实践任务**：解释为什么姓名、电话、SSN 这类 PHI 更适合正则检测而不是 LLM 判断
- **涉及文件**：`src/agents/audit_agent.py`、`src/services/hipaa_service.py`

## 模块 5：GraphRAG 与医疗标准

### 5.1 GraphRAG 基础与内置知识库
- **类型**：理论 + 实践
- **难度**：三星
- **前置知识**：4.3
- **学习目标**：理解 GraphRAG 和传统 RAG 的区别，以及本项目离线知识库如何工作
- **理论要点**：实体、关系、症状到疾病、疾病到 ICD-10、候选排序
- **实践任务**：用 `fever`、`cough`、`chest_pain` 手算候选疾病排序
- **涉及文件**：`src/services/graphrag_service.py`、`docs/04-GraphRAG知识图谱.md`

### 5.2 Neo4j 与 Cypher 入门
- **类型**：理论 + 实践
- **难度**：三星
- **前置知识**：5.1
- **学习目标**：从零理解图数据库的节点、关系、路径查询
- **理论要点**：`MATCH`、节点标签、关系类型、参数化查询、多跳路径
- **实践任务**：读懂 `_find_diseases_by_symptoms_neo4j` 中的 Cypher 查询
- **涉及文件**：`src/services/graphrag_service.py`、`scripts/seed_neo4j_kg.py`

### 5.3 FHIR、ICD-10、DDI、HIPAA 的工程位置
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：4.2、4.4、4.5、4.6
- **学习目标**：把医疗术语和代码模块建立对应关系
- **理论要点**：FHIR 负责互操作数据结构，ICD-10 负责诊断编码，DDI 负责用药安全，HIPAA 负责隐私合规
- **实践任务**：列出每个医疗标准在项目中对应的文件和输出字段
- **涉及文件**：`src/services/fhir_service.py`、`src/services/icd10_service.py`、`src/services/drug_interaction.py`、`src/services/hipaa_service.py`

## 模块 6：前端工作台与流式体验

### 6.1 Vue 工作台页面结构
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：2.1
- **学习目标**：理解前端如何组织页面、路由、组件和全局状态
- **理论要点**：Vue 3、router、Pinia store、组件分层
- **实践任务**：追踪 `AnalysisView` 如何使用 store 和组件展示结果
- **涉及文件**：`frontend/src/App.vue`、`frontend/src/router/index.ts`、`frontend/src/views/AnalysisView.vue`、`frontend/src/stores/analysisStore.ts`

### 6.2 前端 API 调用与 SSE 状态更新
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：6.1、2.2
- **学习目标**：理解前端如何接收后端流式事件并更新五个 Agent 的进度
- **理论要点**：`fetch`、SSE、fallback、stage status、结果合并
- **实践任务**：解释 `applyStreamEvent` 如何处理 `started`、`completed`、`done`、`error`
- **涉及文件**：`frontend/src/api/clinicalApi.ts`、`frontend/src/stores/analysisStore.ts`、`frontend/src/components/StageProgress.vue`

## 模块 7：运行、部署与测试

### 7.1 本地运行与 Docker 编排
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：1.3、2.1
- **学习目标**：理解后端、前端、PostgreSQL、Redis、Neo4j 如何一起运行
- **理论要点**：`uvicorn`、Vite dev server、docker-compose services、端口映射、healthcheck
- **实践任务**：说明 `docker-compose.yml` 中 `api`、`postgres`、`redis`、`neo4j` 的作用
- **涉及文件**：`README-python.md`、`Dockerfile`、`docker-compose.yml`、`frontend/package.json`

### 7.2 后端测试：服务、Pipeline、API
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：4.1、5.1
- **学习目标**：从零理解 pytest 如何保护服务逻辑和 Pipeline 行为
- **理论要点**：单元测试、集成测试、mock、fixture、异步测试
- **实践任务**：阅读 `test_services.py` 和 `test_pipeline_routing.py`，总结它们分别验证什么
- **涉及文件**：`tests/test_services.py`、`tests/test_pipeline_routing.py`、`tests/test_api_stream.py`

### 7.3 前端测试：API 与 Store
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：6.2
- **学习目标**：理解 Vitest 如何测试 API 客户端、Pinia store 和组件结果展示
- **理论要点**：Vitest、jsdom、Vue Test Utils、store action 测试
- **实践任务**：阅读 `analysisStore.test.ts`，说明它如何验证流式事件处理
- **涉及文件**：`frontend/src/api/clinicalApi.test.ts`、`frontend/src/stores/analysisStore.test.ts`、`frontend/src/components/ResultsPanel.test.ts`

## 模块 8：面试表达与扩展设计

### 8.1 面试版系统讲解
- **类型**：理论 + 实践
- **难度**：二星
- **前置知识**：0.1-7.3
- **学习目标**：能用 3 分钟讲清项目背景、架构、流程、亮点和取舍
- **理论要点**：五 Agent 流程、LangGraph 条件路由、GraphRAG、规则审计、SSE 前端进度
- **实践任务**：准备一段“我做了什么、为什么这样设计、遇到什么问题”的项目介绍
- **涉及文件**：`docs/00-项目概览.md`、`docs/02-架构设计详解.md`、`resume_project_intro.md`

### 8.2 常见追问：扩展、可靠性、合规、安全
- **类型**：理论 + 实践
- **难度**：三星
- **前置知识**：8.1
- **学习目标**：能回答面试官对生产化、性能、合规和扩展的追问
- **理论要点**：新增 Agent、持久化 checkpoint、Neo4j 在线模式、Redis 缓存、错误降级、PHI 安全
- **实践任务**：准备 5 个追问回答：如何新增 Agent、如何避免 LLM 幻觉、如何保障合规、如何做流式展示、如何测试
- **涉及文件**：`docs/02-架构设计详解.md`、`docs/04-GraphRAG知识图谱.md`、`docs/06-HIPAA合规设计.md`、`docs/07-部署运维指南.md`
