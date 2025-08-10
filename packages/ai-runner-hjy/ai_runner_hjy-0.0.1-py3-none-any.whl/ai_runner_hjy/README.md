# ai_runner_hjy（AI 调用装配与审计模块）

> 注意（必须阅读）：本模块“只会”从【项目根目录】加载 env 文件（`basic.env`、`mysql.env`）。子目录中的任何 `*.env` 仅作为模板示例，运行期不会读取。
> 运行前会强校验以下必填项，缺失将直接报错并终止：
> - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`
> - 二选一：`MYSQL_AI_DATABASE` 或 `MYSQL_DATABASE`
> - `AI_PEPPER`
> 若缺失，会得到类似错误：
> `RuntimeError: Missing required env variables: MYSQL_HOST, AI_PEPPER. Ensure you have created root-level basic.env/mysql.env and filled values.`

一个可复用的小模块：以“数据库配置驱动”的方式装配并调用 OpenAI Chat Completions 兼容接口（如 qdd/openrouter），并将调用指标与请求/响应 JSON 统一写入 RDS 以便审计与回放。

---

## 适用场景
- 需要“配置切换、代码零改动”的 AI 调用范式（模型/参数/Prompt 全在库里配置）。
- 需要强约束的日志与审计（耗时、状态、token 用量、请求 JSON、响应 JSON）。
- 多项目共用同一套 AI 连接/模型配置，或需要运维同学集中管理配置。

---

## 核心能力
- 按 `config_key` 从 RDS 读取：`ai_connection` → `ai_model` → `ai_param_profile` → `ai_prompt` → `ai_config`。
- 运行时使用 `AI_PEPPER` 在内存里解密 API Key（RDS 仅存 AES‑GCM 密文 JSON）。
- 组装 OpenAI Chat Completions 请求体，参数白名单映射：
  - `TEMPERATURE→temperature`，`TOP_P→top_p`，`MAX_TOKENS→max_tokens`，`STREAM→stream`，`STOP→stop`，`N→n`，`FREQUENCY_PENALTY→frequency_penalty`，`PRESENCE_PENALTY→presence_penalty`
  - 若 `JSON_SCHEMA_ENFORCE=true` 且未在 Prompt 指定 `response_format`，兜底为 `{type:json_object}`
- 统一入库 `ai_call_logs`：
  - 最小：`http_status`、`duration_ms`、token 用量、`response_id`、错误码/信息
  - 扩展：`request_body_json`、`response_body_json`（可选大 JSON；若库未加列则自动回退，只写最小指标）

---

## 目录结构
- `runner.py`：装配 → 调用 → 入库（主要入口）
- `crypto_utils.py`：API Key 解密（AES‑256‑GCM + PBKDF2）
- `core/crud.py`：最小 CRUD（示例实现 `ai_param_profile` 的新增/查询，带幂等校验+统一错误返回）
- `__init__.py`：导出 `run_once / load_envs / get_db_connection`

---

## 环境准备
- 依赖安装（清华源）：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r backend/requirements.txt
```
- 环境变量（模块会从项目根目录按需加载 `basic.env`、`mysql.env`，不覆盖已有环境变量）：
  - 必填：`MYSQL_HOST` `MYSQL_PORT` `MYSQL_USER` `MYSQL_PASSWORD` `MYSQL_AI_DATABASE`(或 `MYSQL_DATABASE`)
  - 必填：`AI_PEPPER`（Pepper，用于从密文 JSON 解密 API Key；严禁入库/泄露）

---

## 最小数据库结构（可直接执行）
> 为了可审计与回放，推荐包含请求/响应两列。若暂不需要，可先省略两列，模块会自动回退到最小日志模式。

```sql
-- 1) 连接表：只存密文 JSON
CREATE TABLE IF NOT EXISTS ai_connection (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  provider ENUM('openai','openrouter','qdd','google','custom') NOT NULL,
  base_url VARCHAR(500) NOT NULL,
  api_key_encrypted JSON NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_conn_name (name)
);

-- 2) 模型：指向连接
CREATE TABLE IF NOT EXISTS ai_model (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  connection_id BIGINT NOT NULL,
  defaults_json JSON NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_model_name (name),
  KEY idx_model_connection (connection_id),
  CONSTRAINT fk_model_connection FOREIGN KEY (connection_id) REFERENCES ai_connection(id)
);

-- 3) 参数白名单（映射到 OpenAI body）
CREATE TABLE IF NOT EXISTS ai_param_profile (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  params_json JSON NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_param_name (name)
);

-- 4) Prompt（可含 variables_json 占位符）
CREATE TABLE IF NOT EXISTS ai_prompt (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  version VARCHAR(20) NOT NULL,
  description TEXT NULL,
  messages_json JSON NOT NULL,
  response_format_json JSON NULL,
  variables_json JSON NULL,
  status ENUM('active','archived') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_prompt_name_version (name, version)
);

-- 5) 配置入口：以 config_key 作为对外接口
CREATE TABLE IF NOT EXISTS ai_config (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  config_key VARCHAR(120) NOT NULL,
  model_id BIGINT NOT NULL,
  param_profile_id BIGINT NULL,
  prompt_id BIGINT NULL,
  description TEXT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_config_key (config_key),
  KEY idx_config_model (model_id),
  KEY idx_config_param (param_profile_id),
  KEY idx_config_prompt (prompt_id),
  CONSTRAINT fk_cfg_model FOREIGN KEY (model_id) REFERENCES ai_model(id),
  CONSTRAINT fk_cfg_param FOREIGN KEY (param_profile_id) REFERENCES ai_param_profile(id),
  CONSTRAINT fk_cfg_prompt FOREIGN KEY (prompt_id) REFERENCES ai_prompt(id)
);

-- 6) 调用日志：最小指标 + 可选大 JSON
CREATE TABLE IF NOT EXISTS ai_call_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  config_key VARCHAR(120) NOT NULL,
  http_status INT NOT NULL,
  duration_ms INT NOT NULL,
  prompt_tokens INT NULL,
  completion_tokens INT NULL,
  total_tokens INT NULL,
  response_id VARCHAR(128) NULL,
  error_code VARCHAR(64) NULL,
  error_message VARCHAR(512) NULL,
  request_body_json JSON NULL,
  response_body_json JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_logs_cfg (config_key),
  KEY idx_logs_time (created_at)
);
```

> 迁移提示（已有库需要补齐唯一约束时）：
> 如已存在 `ai_config` 表但尚未对 `config_key` 加唯一索引，可执行：
>
> ```sql
> ALTER TABLE ai_config.ai_config ADD UNIQUE KEY uk_ai_config_config_key (config_key);
> ```
> 执行后用 `SHOW INDEX FROM ai_config.ai_config` 验证 `Non_unique=0`、`Key_name=uk_ai_config_config_key`、`Column_name=config_key`。

> API Key 加密请使用与本模块一致的 AES‑GCM 方案（见 `crypto_utils.py`），`ai_connection.api_key_encrypted` 列保存密文 JSON：`{"v","alg","iter","salt","nonce","ct"}`（可带 `tag` 兼容旧格式）。

---

## 种子数据（示例）
以 openrouter 为例（仅示意，实际请根据你的提供商修改）。
```sql
-- 连接（先插空密文，随后再 UPDATE 为真实密文）
INSERT INTO ai_connection (name, provider, base_url, api_key_encrypted, is_active)
VALUES ('openrouter_default', 'openrouter', 'https://openrouter.ai/api/v1/chat/completions', JSON_OBJECT(), 1);

-- 模型
ingert INTO ai_model (name, connection_id, is_active)
SELECT 'gemini-2.5-flash', id, 1 FROM ai_connection WHERE name='openrouter_default';

-- 参数白名单
ingert INTO ai_param_profile (name, params_json, is_active)
VALUES ('default_json', JSON_OBJECT('TEMPERATURE',0.2,'MAX_TOKENS',256,'JSON_SCHEMA_ENFORCE', true), 1);

-- Prompt（简单单轮）
INSERT INTO ai_prompt (name, version, description, messages_json, response_format_json, variables_json, status)
VALUES (
  'single_chat_zh','v1','单轮对话 JSON 输出',
  JSON_ARRAY(
    JSON_OBJECT('role','system','content','只输出 JSON，不要多余文本'),
    JSON_OBJECT('role','user','content', JSON_OBJECT('question','{{QUESTION}}'))
  ),
  JSON_OBJECT('type','json_object'),
  JSON_OBJECT('QUESTION','给我一句鼓励的话'),
  'active'
);

-- 配置入口（对外只暴露这个 key）
INSERT INTO ai_config (config_key, model_id, param_profile_id, prompt_id, description, is_active)
SELECT 'gemini25_single_chat', m.id, p.id, pr.id, 'gemini-2.5-flash 单轮对话', 1
FROM ai_model m, ai_param_profile p, ai_prompt pr
WHERE m.name='gemini-2.5-flash' AND p.name='default_json' AND pr.name='single_chat_zh' AND pr.version='v1';
```
> 记得用 `crypto_utils.py` 相同算法生成密文 JSON，并 `UPDATE ai_connection.api_key_encrypted`。

---

## 变量替换（占位符）
- 在 `ai_prompt.variables_json` 与/或 `ai_param_profile.params_json` 中提供变量，模块会按 `{{VARIABLE}}` 替换到 `messages_json`。
- 多模态占位示意：`{{IMAGE_URL}}` / `{{AUDIO_URL}}` / `{{VIDEO_URL}}`（取决于你的消息结构）。

---

## 快速开始
```python
from backend.ai_runner_hjy import run_once
import os

# 方式一：通过环境变量指定（脚本/任务方便）
os.environ['AI_TEST_CONFIG_KEY'] = 'gemini25_single_chat'
run_once()

# 方式二：在代码里显式传入（服务内调用）
run_once('gemini25_single_chat')
```

### 命令行（CLI）用法
无需改代码，直接运行一次：
```bash
python -m backend.ai_runner_hjy --config-key gemini25_single_chat
# 可选参数
python -m backend.ai_runner_hjy --config-key gemini25_single_chat --timeout 30 --max-retries 2
```

### CRUD 最小用法（示例）
```python
from backend.ai_runner_hjy.core.crud import add_param_profile_if_absent, get_param_profile_by_name

# 幂等新增（存在则返回 existed=True）
res, err = add_param_profile_if_absent("default_json", {"TEMPERATURE": 0.2, "MAX_TOKENS": 256})
if err:
    # err 为 (code, message)，例如 ("DB_ERROR", "...") / ("VALIDATION_ERROR", "...")
    raise RuntimeError(err)
print(res)  # {"id": 123, "existed": False}

# 查询
row, err = get_param_profile_by_name("default_json")
if err:
    raise RuntimeError(err)
print(row["params_json"])  # JSON 字符串
```

---

## 日志与错误处理
- 每次调用必写一行 `ai_call_logs`：
  - 成功：`http_status=200/201`、`duration_ms`、`usage.*`、`response_id`，以及两列 JSON（若存在）
  - 失败：`error_code` 为 `HTTP_STATUS_ERROR`（非 2xx）或 `REQUEST_ERROR`（网络/序列化），同时尽量保留响应 JSON 便于排障
- 建议定期审计：慢请求、非 2xx 比例、token 消耗

---

## 常见问题（FAQ）
- Q：为什么没有写入 `request_body_json/response_body_json`？
  - A：请确认你已在 `ai_call_logs` 新增两列；否则模块会回退到最小日志模式（不报错）。
- Q：如何强制只输出 JSON？
  - A：在 Prompt 的 `response_format_json` 指定 `{type:"json_object"}`，或在参数白名单设置 `JSON_SCHEMA_ENFORCE=true`（兜底）。
- Q：API Key 放哪里？
  - A：只以密文 JSON 存在 `ai_connection.api_key_encrypted`。运行时用环境变量 `AI_PEPPER` 解密，明文不会落库/日志。

---

## 与服务集成（示例）
```python
from backend.ai_runner_hjy import run_once

def handle_request(config_key: str):
    # … 业务逻辑
    run_once(config_key)
```
> 若你以前通过 `subprocess` 调脚本，现在可以直接导入函数调用，便于单测与复用。

---

## 许可证与复用
- 内部脚手架，依赖最小、接口清晰，便于在不同项目迁移复用。欢迎在此基础上扩展：
  - 增加缓存/重试/降级策略参数
  - 将请求/响应落 OSS（大体量）并在日志里保存链接
  - 接入更完整的观测与指标