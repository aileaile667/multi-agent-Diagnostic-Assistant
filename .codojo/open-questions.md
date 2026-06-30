# 能力评估问卷

> 本问卷由 AI 根据项目技术栈自动生成，用于评估你的当前水平，以便后续制定个性化学习计划。

## 项目技术栈概览

- 语言：Python 3、TypeScript
- 后端框架：FastAPI、Pydantic v2、Uvicorn
- AI 编排：LangGraph、LangChain、ChatOpenAI 兼容接口
- 核心架构：五 Agent 临床决策流水线，包含 Intake、Diagnosis、Treatment、Coding、Audit
- 状态流转：LangGraph StateGraph、ClinicalState 共享状态、条件路由、MemorySaver checkpoint
- 领域服务：GraphRAG、Neo4j/Cypher、ICD-10-CM、DDI 药物相互作用、FHIR R4、HIPAA Safe Harbor
- 数据与基础设施：PostgreSQL、Redis、Docker、docker-compose、环境变量配置
- 前端：Vue 3、Vite、Pinia、Vue Router、TypeScript、Server-Sent Events
- 测试：pytest、pytest-asyncio、Vitest、Vue Test Utils
- 项目主题：医疗临床辅助决策，多 Agent 协作，结构化输出，合规审计，知识图谱增强诊断

## 评估问题

### Q1: 你对 Python 项目的基础结构和模块导入关系熟悉吗？比如 `src/api`、`src/agents`、`src/services`、`src/models` 分别承担什么职责。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：听说过但没用过

### Q2: 你对 Pydantic 数据模型熟悉吗？能否理解本项目中 `PatientInfo`、`ClinicalState`、`AnalyzeRequest` 这类模型如何校验和序列化数据。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：听说过但没用过

### Q3: 你对 FastAPI 的路由、请求模型、响应模型、异常处理和 Swagger 文档生成熟悉吗？
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：听说过但没用过

### Q4: 你对大语言模型应用开发熟悉吗？比如 prompt、ChatOpenAI 调用、JSON 结构化输出、错误兜底和重试。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：完全不了解

### Q5: 你对 Agent 或多 Agent 系统的概念熟悉吗？能否理解为什么本项目把临床流程拆成五个专用 Agent。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：听说过但没用过

### Q6: 你对 LangGraph 的 StateGraph、节点、边、条件路由、checkpoint 这些概念熟悉吗？
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：用过但不熟练

### Q7: 你对 RAG 或 GraphRAG 熟悉吗？能否理解症状到疾病、疾病到 ICD-10 的知识图谱检索如何辅助诊断。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：听说过但没用过

### Q8: 你对 Neo4j 和 Cypher 查询熟悉吗？比如 `MATCH`、关系遍历、参数化查询、图数据库和关系型数据库的区别。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：完全不了解

### Q9: 你对医疗数据标准和术语熟悉吗？比如 ICD-10-CM、FHIR R4、DDI 药物相互作用、HIPAA PHI 脱敏。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：用过但不熟练

### Q10: 你对前端 Vue 3 + TypeScript + Pinia 熟悉吗？能否理解本项目工作台如何调用 API、接收 SSE 流式事件并更新页面状态。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：听说过但没用过

### Q11: 你对 Docker、docker-compose、环境变量、PostgreSQL、Redis 这类部署和基础设施配置熟悉吗？
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：听说过但没用过

### Q12: 你对测试熟悉吗？比如 pytest 单元测试、接口测试、异步测试，以及前端 Vitest 组件或 store 测试。
- [ ] 完全不了解
- [ ] 听说过但没用过
- [ ] 用过但不熟练
- [ ] 熟练掌握

**你的回答**：完全不了解

## 自由补充

学习目标：理解流程，准备面试

## 评估完成

- 完成时间：2026-06-30 00:00
<!-- ASSESS_DONE -->
