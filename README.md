# Python AI Service - FastAPI Middleware

## Огляд

Це FastAPI middleware сервіс, який передає запити до різних LLM провайдерів (DeepInfra, OpenAI, Ollama) та управляє tool calling з автоматичним виконанням інструментів.

## Архітектура

```
┌─────────────────────────┐
│   Laravel App (PHP)     │
└────────────┬────────────┘
             │ HTTP
             ▼
┌─────────────────────────┐
│  Python AI Service      │
│  (FastAPI Middleware)   │
│                         │
│  ┌─────────────────┐   │
│  │ LLM Service     │   │
│  │ - Chat Logic    │   │
│  │ - Tool Calling  │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ Tool Executor   │   │
│  │ - Calculator    │   │
│  │ - Web Search    │   │
│  └─────────────────┘   │
└────────────┬────────────┘
             │ API Calls
             ▼
┌─────────────────────────┐
│   LLM Providers         │
│  - DeepInfra            │
│  - OpenAI               │
│  - Ollama (Local)       │
└─────────────────────────┘
```

## Структура проекту

```
app/
├── __init__.py
├── config.py                    # Конфігурація з .env
├── main.py                      # FastAPI додаток (moved to root)
├── routers/
│   ├── __init__.py
│   ├── chat.py                  # POST /api/chat
│   └── tools.py                 # GET /api/tools
├── services/
│   ├── __init__.py
│   ├── llm_service.py           # Основна логіка
│   └── tool_executor.py         # Виконання інструментів
├── providers/
│   ├── __init__.py
│   ├── base.py                  # Базовий клас
│   ├── deepinfra.py             # DeepInfra API
│   ├── openai_provider.py       # OpenAI API
│   └── ollama.py                # Ollama API
├── tools/
│   ├── __init__.py              # Tool registry
│   ├── base.py                  # Базовий клас інструмента
│   ├── calculator.py            # Калькулятор
│   └── web_search.py            # Web search (mock)
└── schemas/
    ├── __init__.py
    ├── chat.py                  # ChatMessage, ChatRequest, ChatResponse
    └── tools.py                 # ToolSchema, ToolParameter
```

## Встановлення

### 1. Встановити залежності

```bash
pip install -r requirements.txt
```

### 2. Налаштувати конфігурацію

Скопіювати `.env.example` в `.env` та заповнити необхідні ключі:

```bash
cp .env.example .env
```

```env
DEEPINFRA_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_PROVIDER=deepinfra
DEFAULT_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
```

## Запуск

### Локально

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Через Docker

```bash
docker-compose up
```

Сервіс буде доступний на `http://localhost:8000`

## API Endpoints

### 1. Health Check

```http
GET /api/health
```

Повертає статус сервісу та конфігурацію.

**Відповідь:**
```json
{
  "status": "ok",
  "default_provider": "deepinfra",
  "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
}
```

### 2. Список провайдерів

```http
GET /api/providers
```

Повертає список доступних LLM провайдерів та статус їх налаштування.

**Відповідь:**
```json
{
  "providers": [
    {
      "name": "deepinfra",
      "description": "DeepInfra API",
      "available": true
    },
    {
      "name": "openai",
      "description": "OpenAI API",
      "available": false
    },
    {
      "name": "ollama",
      "description": "Ollama Local",
      "available": true
    }
  ]
}
```

### 3. Список інструментів

```http
GET /api/tools
```

Повертає список доступних інструментів для tool calling.

**Відповідь:**
```json
[
  {
    "name": "calculator",
    "description": "Виконує математичні обчислення. Використовуй для арифметичних операцій.",
    "parameters": [
      {
        "name": "expression",
        "type": "string",
        "description": "Математичний вираз (наприклад, \"2 + 2 * 3\")",
        "required": true
      }
    ]
  },
  {
    "name": "web_search",
    "description": "Шукає актуальну інформацію в інтернеті. Використовуй для пошуку новин, фактів, поточних подій.",
    "parameters": [
      {
        "name": "query",
        "type": "string",
        "description": "Пошуковий запит українською або англійською мовою",
        "required": true
      },
      {
        "name": "max_results",
        "type": "integer",
        "description": "Максимальна кількість результатів (1-10, за замовчуванням 5)",
        "required": false
      },
      {
        "name": "include_content",
        "type": "boolean",
        "description": "Чи включати повний контент сторінок (за замовчуванням true)",
        "required": false
      }
    ]
  },
  {
    "name": "news_search",
    "description": "Шукає свіжі новини та актуальні події.",
    "parameters": [
      {
        "name": "query",
        "type": "string",
        "description": "Пошуковий запит для новин",
        "required": true
      },
      {
        "name": "max_results",
        "type": "integer",
        "description": "Максимальна кількість новин (1-15, за замовчуванням 8)",
        "required": false
      },
      {
        "name": "time_range",
        "type": "string",
        "description": "Період пошуку: 'd' (день), 'w' (тиждень), 'm' (місяць), 'y' (рік)",
        "required": false
      }
    ]
  },
  {
    "name": "web_scraper",
    "description": "Витягує повний контент з конкретної веб-сторінки за URL.",
    "parameters": [
      {
        "name": "url",
        "type": "string",
        "description": "URL веб-сторінки для скрапінгу (повний URL з https://)",
        "required": true
      },
      {
        "name": "extract_links",
        "type": "boolean",
        "description": "Чи витягувати посилання зі сторінки (за замовчуванням false)",
        "required": false
      }
    ]
  },
  {
    "name": "web_summarizer",
    "description": "Шукає інформацію та створює стисле резюме з кількох джерел.",
    "parameters": [
      {
        "name": "query",
        "type": "string",
        "description": "Тема або запит для пошуку та резюмування",
        "required": true
      },
      {
        "name": "max_sources",
        "type": "integer",
        "description": "Максимальна кількість джерел для резюме (1-5, за замовчуванням 3)",
        "required": false
      }
    ]
  }
]
```

### 4. Chat (Основний endpoint)

```http
POST /api/chat
Content-Type: application/json
```

**Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Привіт! Скільки буде 25 * 17 + 33?"
    }
  ],
  "provider": "deepinfra",
  "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
  "tools": ["calculator"],
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "message": {
    "role": "assistant",
    "content": "25 * 17 + 33 = 425 + 33 = 458"
  },
  "tool_calls_made": [
    {
      "tool": "calculator",
      "arguments": {
        "expression": "25 * 17 + 33"
      },
      "result": {
        "result": 458,
        "expression": "25 * 17 + 33"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 50,
    "total_tokens": 200
  },
  "provider": "deepinfra",
  "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
}
```

## Лаштування інструментів

### Додавання нового інструмента

1. Створити файл в `app/tools/` (наприклад, `my_tool.py`):

```python
from app.schemas.tools import ToolParameter
from app.tools.base import BaseTool

class MyTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "Опис інструмента"
    
    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="param1",
                type="string",
                description="Описання параметра",
                required=True
            )
        ]
    
    async def execute(self, **kwargs) -> dict:
        param1 = kwargs.get("param1")
        # Реалізація логіки
        return {"result": "успіх"}
```

2. Зареєструвати в `app/tools/__init__.py`:

```python
from app.tools.my_tool import MyTool

_registry.register(MyTool())
```

## Tool Calling Loop

Сервіс автоматично виконує tool calling в циклі:

1. LLM отримує запит з інструментами
2. Якщо LLM визначає, що потрібен інструмент:
   - Повертає tool call з аргументами
3. Сервіс виконує інструмент
4. Додає результат до контексту
5. Викликає LLM знову з результатом
6. Повторює процес до 10 разів або поки LLM не закінчить

## Логування

Сервіс логує всі операції:
- Вхідні запити
- Вибір провайдера і моделі
- Execution tool calls
- Помилки та винятки

Логи у форматі:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Приклади використання

### cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Simple chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Привіт!"}],
    "provider": "deepinfra"
  }'

# Chat with calculator
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Скільки буде 2 + 2?"}],
    "provider": "deepinfra",
    "tools": ["calculator"]
  }'

# Web search
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Знайди останні новини про штучний інтелект"}],
    "provider": "deepinfra",
    "tools": ["web_search"]
  }'

# News search
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Які новини сьогодні в технологіях?"}],
    "provider": "deepinfra",
    "tools": ["news_search"]
  }'

# Web scraping
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Витягни контент з https://example.com"}],
    "provider": "deepinfra",
    "tools": ["web_scraper"]
  }'

# Web summarization
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Створи резюме про FastAPI з кількох джерел"}],
    "provider": "deepinfra",
    "tools": ["web_summarizer"]
  }'
```

### Python

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/chat",
        json={
            "messages": [{"role": "user", "content": "Привіт!"}],
            "provider": "deepinfra"
        }
    )
    print(response.json())
```

### JavaScript

```javascript
const response = await fetch("http://localhost:8000/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    messages: [{ role: "user", content: "Привіт!" }],
    provider: "deepinfra"
  })
});

const data = await response.json();
console.log(data);
```

## Налаштування провайдерів

### DeepInfra

Найпростіший варіант для швидкого старту. Вимагає API ключ.

1. Зареєструватися на https://deepinfra.com
2. Отримати API ключ
3. Встановити `DEEPINFRA_API_KEY` в `.env`

### OpenAI

Для використання GPT моделей.

## ⚠️ Проблема: Модель не використовує інструменти (Tools)

Якщо ваша модель не викликає інструменти, це може бути через кілька причин:

### 1. **Модель не підтримує Function Calling**

Не всі моделі підтримують function calling. Для роботи з інструментами потрібні спеціально навчені моделі.

#### ✅ Моделі, які ПІДТРИМУЮТЬ function calling:

**Ollama (локальні):**
- `qwen2.5:7b` ⭐ **РЕКОМЕНДОВАНА** - найкраща підтримка tools
- `llama3.1:8b` - офіційна підтримка від Meta
- `mistral:7b-instruct-v0.3` - добра підтримка
- `firefunction-v2` - спеціалізована для function calling

**DeepInfra (хмарні):**
- `meta-llama/Llama-3.3-70B-Instruct-Turbo` ⭐ **РЕКОМЕНДОВАНА**
- `meta-llama/Llama-3.1-70B-Instruct`
- `Qwen/Qwen2.5-72B-Instruct`

**OpenAI:**
- `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`

#### ❌ Моделі, які НЕ підтримують:
- `gemma2:2b`, `gemma3:4b` - занадто малі
- `llama2` - старша версія
- Більшість моделей < 7B параметрів

### 2. **Ollama не запущений**

```bash
# Перевірка
curl http://127.0.0.1:11434/api/tags

# Якщо не працює - запустіть
ollama serve

# В іншому терміналі завантажте модель
ollama pull qwen2.5:7b
```

### 3. **Проблема з підключенням**

Якщо бачите помилку "Connection error" або "Temporary failure in name resolution":

```bash
# Перевірте чи запущений Ollama
ps aux | grep ollama

# Перевірте порт
netstat -tlnp | grep 11434

# Спробуйте перезапустити
pkill ollama
ollama serve
```

### 4. **Налаштування для кращої роботи з інструментами**

Наш сервіс автоматично додає system prompt для інструментів, але ви можете налаштувати:

```python
# У .env файлі
DEFAULT_PROVIDER=ollama
DEFAULT_MODEL=qwen2.5:7b

# Або у запиті
ChatRequest(
    messages=[...],
    provider="ollama",
    model="qwen2.5:7b",  # Модель з підтримкою tools
    tools=["calculator", "web_search"],
    temperature=0.1  # Низька temperature для стабільності
)
```

## Тестування інструментів

### Швидкий тест

```bash
# Базовий тест (перевіряє формат і підключення)
python3 test_tools_usage.py

# Розширений тест (з різними провайдерами)
python3 test_tools_comprehensive.py
```

### Запуск сервера і тест через API

```bash
# Термінал 1: Запустити Ollama
ollama serve

# Термінал 2: Запустити AI сервіс
uvicorn main:app --reload

# Термінал 3: Тест через curl
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Скільки буде 125 * 47?"}],
    "provider": "ollama",
    "model": "qwen2.5:7b",
    "tools": ["calculator"],
    "temperature": 0.1
  }'
```

## Веб-скрапінг інструменти

Проект включає потужні інструменти для отримання інформації з інтернету:

### Доступні інструменти:

1. **web_search** - Пошук в інтернеті (DuckDuckGo)
2. **news_search** - Пошук новин
3. **web_scraper** - Скрапінг конкретної сторінки
4. **web_summarizer** - Пошук і створення резюме з кількох джерел

### Приклади:

```python
# Пошук актуальної інформації
ChatRequest(
    messages=[{"role": "user", "content": "Яка погода в Києві?"}],
    tools=["web_search"]
)

# Новини
ChatRequest(
    messages=[{"role": "user", "content": "Останні новини про AI"}],
    tools=["news_search"]
)

# Скрапінг сторінки
ChatRequest(
    messages=[{"role": "user", "content": "Витягни текст з https://example.com"}],
    tools=["web_scraper"]
)

# Резюме з кількох джерел
ChatRequest(
    messages=[{"role": "user", "content": "Зроби резюме про Bitcoin"}],
    tools=["web_summarizer"]
)
```

## Додаткова інформація

- 📖 **Детальний гайд по tools:** [TOOLS_GUIDE.md](TOOLS_GUIDE.md)
- 🌐 **Інформація про веб-скрапінг:** [WEB_SCRAPING.md](WEB_SCRAPING.md)
- 📋 **Гайдлайни розробки:** [GUIDELINE.md](GUIDELINE.md)

## Troubleshooting

### Ollama не підключається

```bash
# Помилка: Connection error
# Рішення 1: Перевірте чи запущений
ollama serve

# Рішення 2: Перевірте конфігурацію
echo $OLLAMA_HOST  # Має бути 127.0.0.1:11434

# Рішення 3: Перезапустіть
pkill ollama && ollama serve
```

### Модель не використовує інструменти

```bash
# 1. Перевірте модель
ollama list  # Має бути qwen2.5:7b або llama3.1:8b

# 2. Завантажте правильну модель
ollama pull qwen2.5:7b

# 3. Оновіть Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 4. Перевірте версію (потрібна >= 0.1.26)
ollama --version
```

### Веб-скрапінг не працює

```bash
# Встановіть залежності
pip install beautifulsoup4 lxml aiohttp

# Або оновіть пакет для пошуку
pip install --upgrade ddgs

# Перевірте налаштування
python3 test_web_intelligence.py
```

## Контакти і підтримка

Якщо виникли проблеми або питання:
1. Перегляньте [TOOLS_GUIDE.md](TOOLS_GUIDE.md)
2. Запустіть тести: `python3 test_tools_usage.py`
3. Перевірте логи сервісу

### OpenAI

Для використання GPT моделей.

1. Зареєструватися на https://platform.openai.com
2. Отримати API ключ
3. Встановити `OPENAI_API_KEY` в `.env`
4. Передавати `provider: "openai"` в запитах

### Ollama

Для локального запуску моделей на машині.

1. Встановити Ollama з https://ollama.ai
2. Запустити Ollama сервер: `ollama serve`
3. Завантажити модель: `ollama pull llama2`
4. Встановити `OLLAMA_BASE_URL` в `.env` (default: http://localhost:11434)
5. Передавати `provider: "ollama"` в запитах

## Обмеження та Примітки

- Tool calling loop обмежена 10 ітеціями щоб уникнути нескінченних циклів
- Калькулятор використовує обмежений eval для безпеки
- Web search поки що повертає mock результати
- Всі операції є асинхронні для максимальної продуктивності
- CORS включений для всіх походжень (для розробки)

## Розвиток

### Плани

- [x] Інтегрування реального web search (DuckDuckGo) ✅ Виконано
- [x] Веб-скрапінг з витягуванням контенту ✅ Виконано  
- [x] Пошук новин з фільтрацією за датами ✅ Виконано
- [x] Автоматичне резюмування з кількох джерел ✅ Виконано
- [ ] Підтримка JavaScript сайтів (Selenium/Playwright)
- [ ] Інтеграція з Google Search API
- [ ] Додавання більш складних інструментів (база даних, файлова система)
- [ ] Streaming відповідей
- [ ] Кешування запитів та результатів пошуку
- [ ] Rate limiting для веб-запитів
- [ ] Аутентифікація та авторизація
- [ ] Моніторинг та аналітика веб-трафіку

## Ліцензія

MIT

## Підтримка

Для питань та проблем створіть issue на GitHub або зв'яжіться з розробниками.

