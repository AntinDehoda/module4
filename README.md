# Advanced CrewAI Demo з MCP Sequential Thinking

Демонстрація CrewAI агента з:
- ⚡ Паралельним запуском задач
- 🧠 Інтеграцією MCP Sequential Thinking для структурованого аналізу
- 🔍 Реальним пошуком новин через DuckDuckGo

## 🎯 Що робить цей агент?

1. **Паралельний пошук** - шукає новини з 3 джерел одночасно (BBC, CNN, Reuters)
2. **Структурований аналіз** - використовує MCP sequential-thinking для глибокого аналізу
3. **Синтез висновків** - генерує комплексний звіт з рекомендаціями

## 🧠 MCP Sequential Thinking

Sequential Thinking Server - це MCP інструмент для:
- Розділення складних задач на керовані етапи
- Переформулювання та уточнення процесу мислення
- Генерування та перевірки гіпотез
- Динамічного коригування кроків аналізу

### Параметри інструменту:

```python
{
    "thought": "Поточний крок мислення",
    "nextThoughtNeeded": true/false,
    "thoughtNumber": 1,
    "totalThoughts": 5,
    "isRevision": false,
    "branchFromThought": null,
    "needsMoreThoughts": false
}
```

## 📋 Структура

```
advanced_crewai_demo/
├── README.md                          # Ця документація
├── requirements.txt                   # Залежності
├── config.py                          # Конфігурація
├── parallel_agent_with_mcp.py        # Основний агент
└── mcp_thinking_tool.py              # MCP wrapper для CrewAI
```

## 🚀 Встановлення

```bash
# 1. Встановіть залежності
pip install -r requirements.txt

# 2. Створіть .env файл
cp ../.env.example .env
# Додайте OPENAI_API_KEY

# 3. Запустіть агента
python parallel_agent_with_mcp.py
```

## 💡 Приклади використання

### Базовий запуск
```bash
python parallel_agent_with_mcp.py
```

### З власною темою
```python
from parallel_agent_with_mcp import run_advanced_analysis

result = run_advanced_analysis(
    topic="quantum computing breakthrough",
    enable_thinking=True
)
```

## 🔧 Налаштування MCP

MCP sequential-thinking вже доступний в Claude Code. Для локального використання:

### NPX метод:
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

### Docker метод:
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

## 📚 Додаткові ресурси

- [MCP Sequential Thinking GitHub](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [CrewAI Documentation](https://docs.crewai.com)
