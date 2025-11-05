# Advanced CrewAI з MCP Sequential Thinking

Демонстрація CrewAI агента з:
- ⚡ Паралельним запуском задач
- 🧠 Інтеграцією MCP Sequential Thinking сервера
- 🔍 Реальним пошуком новин через DuckDuckGo

## 🎯 Що робить цей агент?

1. **Паралельний пошук** - шукає новини з 3 джерел одночасно (BBC, CNN, Reuters)
2. **Структурований аналіз** - використовує MCP sequential-thinking сервер для глибокого аналізу
3. **Синтез висновків** - генерує комплексний звіт з рекомендаціями

## 📊 Архітектура

### 5-Агентна система:

```
┌─────────────────┐
│ BBC Researcher  │─┐
└─────────────────┘ │
                    │
┌─────────────────┐ ▼           ┌──────────────────┐
│ CNN Researcher  │────────────►│ Senior Analyst   │
└─────────────────┘             │ (з MCP thinking) │
                    ▲           └────────┬─────────┘
┌─────────────────┐ │                    │
│Reuters Researcher│─┘                   ▼
└─────────────────┘            ┌──────────────────┐
                               │ Report Synthesizer│
                               └──────────────────┘
```

### MCP Integration:

```
CrewAI Agent → MCP Bridge → MCP Client → MCP Server
                (sync↔async)  (Python SDK)  (npx/@modelcontextprotocol)
```

## 📋 Структура проекту

```
module4/
├── README.md                        # Документація
├── requirements.txt                 # Залежності Python
├── .env.example                     # Шаблон конфігурації
├── .gitignore                       # Git виключення
│
├── config.py                        # Управління налаштуваннями
├── parallel_agent_with_mcp.py      # 🎯 Основний агент (5 агентів)
├── mcp_client.py                   # MCP client (async)
└── mcp_bridge.py                   # Міст async→sync для CrewAI
```

## 🚀 Встановлення

### Крок 1: Python залежності

```bash
pip install -r requirements.txt
```

**Залежності:**
- `crewai>=0.80.0` - Multi-agent framework
- `langchain>=1.0.0` - LLM orchestration
- `langchain-openai>=1.0.0` - OpenAI integration
- `duckduckgo-search>=5.0.0` - News search
- `mcp>=1.0.0` - MCP Python SDK
- `sequential-thinking-mcp>=0.1.0` - MCP sequential thinking
- `python-dotenv>=1.0.0` - Environment variables

### Крок 2: Node.js (для MCP сервера)

MCP Sequential Thinking сервер запускається через npx.

**macOS (Homebrew):**
```bash
brew install node
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows:**
Завантажте з [nodejs.org](https://nodejs.org/)

**Перевірка:**
```bash
node --version   # Повинно бути v18+
npx --version    # Повинно працювати
```

### Крок 3: Конфігурація

```bash
cp .env.example .env
```

Відредагуйте `.env`:
```bash
# Обов'язково
OPENAI_API_KEY=your-openai-api-key-here

# Опціонально
DEFAULT_MODEL=gpt-4o-mini
TEMPERATURE=0.7
ENABLE_MCP_THINKING=true
MAX_SEARCH_RESULTS=3
```

## 🎮 Використання

### Базовий запуск

```bash
python parallel_agent_with_mcp.py
```

При першому запуску MCP сервер завантажиться автоматично через npx.

**Очікуваний вивід:**
```
✅ Використовується СПРАВЖНІЙ MCP Sequential Thinking сервер
✅ Підключено до MCP Sequential Thinking сервера

🚀 ADVANCED CREWAI: Паралельний пошук + MCP Sequential Thinking
================================================================================

📋 Створення агентів...

🔍 Тема аналізу: 'artificial intelligence breakthrough'
🧠 MCP Sequential Thinking: ✓ Enabled
📡 MCP Server: npx @modelcontextprotocol/server-sequential-thinking
   └─ Пошук з BBC, CNN, Reuters (паралельно)

⚡ Запуск паралельного пошуку та аналізу...
```

### Програмне використання

```python
from parallel_agent_with_mcp import run_advanced_analysis

# Запустити аналіз
result = run_advanced_analysis(
    topic="quantum computing breakthrough",
    enable_thinking=True
)

print(result['result'])
print(f"Час виконання: {result['duration']:.2f}с")
print(f"MCP thinking: {result['thinking_enabled']}")
```

### З власною конфігурацією

```python
from config import Config

# Кастомна конфігурація
Config.DEFAULT_MODEL = "gpt-4"
Config.TEMPERATURE = 0.9
Config.MAX_SEARCH_RESULTS = 5

# Запуск
result = run_advanced_analysis(topic="climate change policy")
```

## 🧪 Тестування

### Тест MCP клієнта

```bash
python mcp_client.py
```

**Очікуваний результат:**
```
🔌 Підключення до MCP сервера...
✅ Підключено до MCP Sequential Thinking сервера

📋 Доступні інструменти:
  - sequential_thinking: ...

🧠 Тест sequential thinking:
Крок 1: ✓ Крок 1/3 записано...
Крок 2: ✓ Крок 2/3 записано...
Крок 3: ✓ Крок 3/3 записано...

🔌 Відключено від MCP сервера
```

### Тест MCP bridge

```bash
python mcp_bridge.py
```

Перевіряє:
- Запуск MCP bridge в окремому потоці
- Sync/async конвертацію
- CrewAI @tool обгортки
- Cleanup при завершенні

### Тест конфігурації

```bash
python config.py
```

## 🔧 Налаштування MCP сервера

### Для Claude Desktop

Додайте в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

### Для Docker

```json
{
  "mcpServers": {
    "sequentialthinking": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "mcp/sequentialthinking"]
    }
  }
}
```

## 🐛 Troubleshooting

### "npx command not found"

**Проблема:** Node.js не встановлений
**Рішення:** Встановіть Node.js (див. Крок 2 встановлення)

```bash
# macOS
brew install node

# Перевірка
npx --version
```

### "Cannot connect to MCP server"

**Проблема:** MCP сервер не запустився
**Рішення:** Перевірте npx вручну:

```bash
npx -y @modelcontextprotocol/server-sequential-thinking --help
```

Якщо працює - проблема з підключенням. Перевірте логи.

### "Module 'mcp' not found"

**Проблема:** MCP SDK не встановлений
**Рішення:**

```bash
pip install mcp>=1.0.0 sequential-thinking-mcp>=0.1.0
```

### "OpenAI API key not found"

**Проблема:** OPENAI_API_KEY не встановлений
**Рішення:**

```bash
# В .env файлі
OPENAI_API_KEY=your-api-key-here

# Або через export
export OPENAI_API_KEY="your-api-key-here"
```

### Повільна робота

**Причина:** MCP сервер додає overhead для міжпроцесної комунікації
**Нормально:** Перший запуск може бути повільнішим (завантаження сервера)

**Оптимізація:**
- Використовуйте кешування результатів
- Зменшіть MAX_SEARCH_RESULTS
- Використовуйте швидшу модель (gpt-3.5-turbo)

## 📚 Як працює MCP Sequential Thinking

### Інструмент `sequential_thinking`

```python
sequential_thinking(
    thought="Аналізуємо дані...",
    thought_number=1,
    total_thoughts=5,
    next_thought_needed=True,
    is_revision=False,        # Переопрацювання кроку
    revises_thought=None,     # Номер кроку для перегляду
    branch_from_thought=None, # Гілка від кроку
    branch_id=None,           # ID гілки
    needs_more_thoughts=False # Потрібні додаткові кроки
)
```

### Приклад використання агентом

```
Крок 1: Визначаємо основні теми в новинах
Крок 2: Шукаємо унікальні інсайти з кожного джерела
Крок 3: Виявляємо протиріччя (якщо є)
Крок 4: Аналізуємо можливі наслідки
Крок 5: Формулюємо висновки
```

## 📊 Потік даних

```
1. Parallel Search Phase
   ├─ BBC Agent   → DuckDuckGo Search → BBC News
   ├─ CNN Agent   → DuckDuckGo Search → CNN News
   └─ Reuters     → DuckDuckGo Search → Reuters News

2. Analysis Phase (MCP Sequential Thinking)
   └─ Senior Analyst Agent
      ├─ Step 1: Identify common themes
      ├─ Step 2: Find unique insights
      ├─ Step 3: Detect contradictions
      ├─ Step 4: Analyze implications
      └─ Step 5: Form conclusions

3. Synthesis Phase
   └─ Report Synthesizer
      ├─ Executive Summary
      ├─ Key Findings
      ├─ Main Conclusions
      └─ Recommendations
```

## 💡 Поради

1. **Для швидших тестів:** Встановіть `MAX_SEARCH_RESULTS=1` в .env
2. **Для глибшого аналізу:** Збільшіть `total_thoughts` в інструкціях агента
3. **Для економії токенів:** Використовуйте `gpt-4o-mini` замість `gpt-4`
4. **Для продакшену:** Додайте retry логіку для MCP підключення

## 🔗 Додаткові ресурси

- [MCP Sequential Thinking Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [CrewAI Documentation](https://docs.crewai.com)

## 📝 License

MIT License
