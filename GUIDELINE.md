# GUIDELINE: Реалізація Python AI Service

## Загальний опис

Створити FastAPI сервіс, який служить middleware між Laravel додатком та різними LLM провайдерами (DeepInfra, OpenAI, Ollama). Сервіс повинен підтримувати tool calling з автоматичним виконанням інструментів.

---

## Крок 1: Ініціалізація проекту

### 1.1 Створити структуру папок

```
app/
├── __init__.py
├── main.py
├── config.py
├── routers/
│   ├── __init__.py
│   ├── chat.py
│   └── tools.py
├── services/
│   ├── __init__.py
│   ├── llm_service.py
│   └── tool_executor.py
├── providers/
│   ├── __init__.py
│   ├── base.py
│   ├── deepinfra.py
│   ├── openai_provider.py
│   └── ollama.py
├── tools/
│   ├── __init__.py
│   ├── base.py
│   ├── web_search.py
│   └── calculator.py
└── schemas/
    ├── __init__.py
    ├── chat.py
    └── tools.py
```

### 1.2 Створити requirements.txt

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
httpx>=0.26.0
openai>=1.10.0
python-dotenv>=1.0.0
```

### 1.3 Створити .env.example

```
DEEPINFRA_API_KEY=your_deepinfra_key
OPENAI_API_KEY=your_openai_key
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_PROVIDER=deepinfra
DEFAULT_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
```

---

## Крок 2: Базова конфігурація

### 2.1 Файл `app/config.py`

- Використати `pydantic-settings` для конфігурації
- Завантажувати змінні з `.env` файлу
- Поля:
  - `deepinfra_api_key: str | None`
  - `openai_api_key: str | None`
  - `ollama_base_url: str` (default: "http://localhost:11434")
  - `default_provider: str` (default: "deepinfra")
  - `default_model: str` (default: "meta-llama/Llama-3.3-70B-Instruct-Turbo")

### 2.2 Файл `app/main.py`

- Створити FastAPI додаток
- Підключити роутери (chat, tools)
- Додати CORS middleware
- Додати health check endpoint `GET /api/health`
- Додати endpoint `GET /api/providers` для списку провайдерів

---

## Крок 3: Pydantic Schemas

### 3.1 Файл `app/schemas/chat.py`

```python
# ChatMessage
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None
    name: str | None = None

# ChatRequest
class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    provider: str | None = None  # deepinfra, openai, ollama
    model: str | None = None
    tools: list[str] = []  # ["web_search", "calculator"]
    stream: bool = False
    max_tokens: int | None = None
    temperature: float = 0.7

# ToolCallInfo
class ToolCallInfo(BaseModel):
    tool: str
    arguments: dict
    result: Any

# ChatResponse
class ChatResponse(BaseModel):
    success: bool
    message: ChatMessage
    tool_calls_made: list[ToolCallInfo] = []
    usage: dict | None = None
    provider: str
    model: str
```

### 3.2 Файл `app/schemas/tools.py`

```python
# ToolParameter
class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True

# ToolSchema
class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameter]
```

---

## Крок 4: Base Provider

### 4.1 Файл `app/providers/base.py`

- Створити абстрактний клас `BaseLLMProvider`
- Методи:
  - `async def chat(messages, tools, **kwargs) -> dict` - абстрактний
  - `def format_tools(tools: list[ToolSchema]) -> list[dict]` - конвертація в OpenAI format
  - `def get_available_models() -> list[str]` - абстрактний

---

## Крок 5: Реалізація провайдерів

### 5.1 Файл `app/providers/deepinfra.py`

- Наслідувати `BaseLLMProvider`
- Використовувати OpenAI SDK з `base_url="https://api.deepinfra.com/v1/openai"`
- Реалізувати `chat()` метод
- Підтримувати tool calling (OpenAI-compatible format)
- Доступні моделі:
  - `meta-llama/Llama-3.3-70B-Instruct-Turbo`
  - `meta-llama/Llama-3.1-8B-Instruct`
  - `Qwen/Qwen2.5-72B-Instruct`

### 5.2 Файл `app/providers/openai_provider.py`

- Наслідувати `BaseLLMProvider`
- Використовувати стандартний OpenAI SDK
- Доступні моделі:
  - `gpt-4o`
  - `gpt-4o-mini`
  - `gpt-3.5-turbo`

### 5.3 Файл `app/providers/ollama.py`

- Наслідувати `BaseLLMProvider`
- Використовувати OpenAI SDK з `base_url` з конфігурації + `/v1`
- Динамічно отримувати список моделей через Ollama API

---

## Крок 6: Base Tool

### 6.1 Файл `app/tools/base.py`

- Створити абстрактний клас `BaseTool`
- Властивості:
  - `name: str` - унікальний ідентифікатор
  - `description: str` - опис для LLM
  - `parameters: list[ToolParameter]` - параметри
- Методи:
  - `async def execute(**kwargs) -> Any` - абстрактний
  - `def get_schema() -> ToolSchema` - повертає схему інструмента
  - `def to_openai_format() -> dict` - конвертація в OpenAI tool format

---

## Крок 7: Реалізація інструментів

### 7.1 Файл `app/tools/calculator.py`

- Наслідувати `BaseTool`
- `name = "calculator"`
- `description = "Виконує математичні обчислення. Використовуй для арифметичних операцій."`
- Параметри:
  - `expression: str` - математичний вираз (наприклад, "2 + 2 * 3")
- Реалізація:
  - Безпечно виконати математичний вираз (використати `ast.literal_eval` або обмежений `eval`)
  - Повернути результат обчислення

### 7.2 Файл `app/tools/web_search.py`

- Наслідувати `BaseTool`
- `name = "web_search"`
- `description = "Шукає інформацію в інтернеті. Використовуй для актуальної інформації."`
- Параметри:
  - `query: str` - пошуковий запит
- Реалізація:
  - Поки що mock реалізація (повертати заглушку)
  - TODO: інтегрувати з реальним API (DuckDuckGo, Brave Search, тощо)

---

## Крок 8: Tool Registry

### 8.1 Файл `app/tools/__init__.py`

- Створити `ToolRegistry` клас
- Методи:
  - `register(tool: BaseTool)` - зареєструвати інструмент
  - `get(name: str) -> BaseTool | None` - отримати за назвою
  - `get_all() -> list[BaseTool]` - отримати всі
  - `get_by_names(names: list[str]) -> list[BaseTool]` - отримати за списком назв
- Автоматично реєструвати всі інструменти при імпорті

---

## Крок 9: Tool Executor Service

### 9.1 Файл `app/services/tool_executor.py`

- Клас `ToolExecutor`
- Методи:
  - `async def execute_tool_calls(tool_calls: list[dict]) -> list[dict]`
    - Отримати tool calls з відповіді LLM
    - Для кожного tool call:
      - Знайти інструмент в registry
      - Виконати з переданими аргументами
      - Зібрати результати
    - Повернути список результатів у форматі для LLM

---

## Крок 10: LLM Service

### 10.1 Файл `app/services/llm_service.py`

- Клас `LLMService`
- Ін'єкція залежностей: `ToolRegistry`, `ToolExecutor`
- Методи:
  - `get_provider(name: str) -> BaseLLMProvider` - фабрика провайдерів
  - `async def chat(request: ChatRequest) -> ChatResponse` - основний метод

### 10.2 Логіка методу `chat()`

```
1. Отримати провайдер за назвою (або default)
2. Отримати інструменти за назвами з request.tools
3. Конвертувати інструменти в OpenAI format
4. Викликати provider.chat(messages, tools)
5. LOOP (max 10 ітерацій):
   a. Якщо відповідь містить tool_calls:
      - Виконати всі tool calls через ToolExecutor
      - Додати результати до messages як tool role
      - Викликати provider.chat() знову
   b. Якщо відповідь НЕ містить tool_calls:
      - Вийти з циклу
6. Сформувати ChatResponse з фінальною відповіддю
```

---

## Крок 11: Роутери

### 11.1 Файл `app/routers/chat.py`

- `POST /api/chat` - основний endpoint
  - Прийняти `ChatRequest`
  - Викликати `LLMService.chat()`
  - Повернути `ChatResponse`

### 11.2 Файл `app/routers/tools.py`

- `GET /api/tools` - список доступних інструментів
  - Повернути список `ToolSchema`

---

## Крок 12: Docker

### 12.1 Створити `Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 12.2 Створити `docker-compose.yml`

```yaml
services:
  ai-service:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Крок 13: Тестування

### 13.1 Ручне тестування

Після запуску сервісу, протестувати через curl або HTTP client:

```bash
# Health check
curl http://localhost:8000/api/health

# Список провайдерів
curl http://localhost:8000/api/providers

# Список інструментів
curl http://localhost:8000/api/tools

# Chat без інструментів
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Привіт!"}],
    "provider": "deepinfra"
  }'

# Chat з калькулятором
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Скільки буде 25 * 17 + 33?"}],
    "provider": "deepinfra",
    "tools": ["calculator"]
  }'
```

---

## Порядок реалізації (рекомендований)

1. **Спочатку**: config.py, main.py (базовий), schemas/
2. **Потім**: providers/base.py, providers/deepinfra.py
3. **Далі**: tools/base.py, tools/calculator.py, tools/__init__.py (registry)
4. **Після**: services/tool_executor.py, services/llm_service.py
5. **Наприкінці**: routers/chat.py, routers/tools.py
6. **Фінал**: Docker файли, тестування

---

## Важливі примітки

- Використовувати `async/await` для всіх I/O операцій
- Всі провайдери використовують OpenAI SDK (він підтримує різні base_url)
- Tool calling loop обмежити 10 ітераціями щоб уникнути нескінченних циклів
- Логувати всі tool calls для дебагу
- Обробляти помилки gracefully (повертати error response замість 500)

