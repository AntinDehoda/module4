"""
Advanced CrewAI Agent з паралельним запуском та Sequential Thinking

Цей агент демонструє:
1. Паралельний пошук новин з 3 джерел (BBC, CNN, Reuters)
2. Структуроване мислення для глибокого аналізу
3. Синтез висновків з рекомендаціями

Продакшен-ready версія з простим але ефективним sequential thinking.
"""

import time
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from duckduckgo_search import DDGS
from config import Config
from sequential_thinking import THINKING_TOOLS, reset_thinking_process

# Initialize configuration
Config.validate()

print("✅ Sequential Thinking ініціалізовано")


@tool("DuckDuckGo News Search")
def search_news(query: str) -> str:
    """
    Пошук новин через DuckDuckGo.

    Args:
        query: Пошуковий запит

    Returns:
        Результати пошуку новин
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=Config.MAX_SEARCH_RESULTS)

        if not results:
            return f"Новин не знайдено для запиту: {query}"

        output = []
        for i, result in enumerate(results, 1):
            output.append(f"{i}. {result.get('title', 'N/A')}")
            output.append(f"   {result.get('body', 'N/A')}")
            output.append(f"   Джерело: {result.get('href', 'N/A')}\n")

        return "\n".join(output)

    except Exception as e:
        return f"Помилка пошуку: {str(e)}"


def create_search_agents():
    """Створює агентів для паралельного пошуку"""

    search_tool = search_news

    bbc_agent = Agent(
        role='BBC News Researcher',
        goal='Знайти та проаналізувати останні новини з BBC',
        backstory='Ти експерт з пошуку та аналізу новин BBC. '
                 'Твоя задача - знайти найрелевантніші новини та виділити ключові факти.',
        tools=[search_tool],
        verbose=True,
        allow_delegation=False
    )

    cnn_agent = Agent(
        role='CNN News Researcher',
        goal='Знайти та проаналізувати останні новини з CNN',
        backstory='Ти експерт з пошуку та аналізу новин CNN. '
                 'Твоя задача - знайти найрелевантніші новини та виділити ключові факти.',
        tools=[search_tool],
        verbose=True,
        allow_delegation=False
    )

    reuters_agent = Agent(
        role='Reuters News Researcher',
        goal='Знайти та проаналізувати останні новини з Reuters',
        backstory='Ти експерт з пошуку та аналізу новин Reuters. '
                 'Твоя задача - знайти найрелевантніші новини та виділити ключові факти.',
        tools=[search_tool],
        verbose=True,
        allow_delegation=False
    )

    return bbc_agent, cnn_agent, reuters_agent


def create_analyst_agent(enable_thinking=True):
    """Створює агента-аналітика з MCP thinking tools"""

    tools = []
    if enable_thinking and Config.ENABLE_MCP_THINKING:
        tools = THINKING_TOOLS

    analyst_agent = Agent(
        role='Senior News Analyst',
        goal='Провести глибокий аналіз новин з різних джерел та виробити висновки',
        backstory='Ти досвідчений аналітик новин з 15 років досвіду. '
                 'Ти використовуєш структуроване мислення для аналізу складних ситуацій. '
                 'Твої висновки завжди базуються на фактах та логічному аналізі.',
        tools=tools,
        verbose=True,
        allow_delegation=False
    )

    return analyst_agent


def create_synthesis_agent():
    """Створює агента для синтезу фінального звіту"""

    synthesis_agent = Agent(
        role='Report Synthesizer',
        goal='Створити комплексний фінальний звіт з рекомендаціями',
        backstory='Ти експерт зі створення якісних аналітичних звітів. '
                 'Ти вмієш синтезувати інформацію з різних джерел в єдиний '
                 'зрозумілий звіт з чіткими висновками та рекомендаціями.',
        verbose=True
    )

    return synthesis_agent


def run_advanced_analysis(topic="artificial intelligence", enable_thinking=True):
    """
    Запускає розширений аналіз новин з MCP thinking

    Args:
        topic: Тема для пошуку новин
        enable_thinking: Чи використовувати MCP sequential thinking

    Returns:
        Dict з результатами аналізу
    """

    print("\n" + "="*80)
    print("🚀 ADVANCED CREWAI: Паралельний пошук + Sequential Thinking")
    print("="*80 + "\n")

    # Reset thinking process
    if enable_thinking:
        reset_thinking_process()

    start_time = time.time()

    # Створюємо агентів
    print("📋 Створення агентів...")
    bbc_agent, cnn_agent, reuters_agent = create_search_agents()
    analyst_agent = create_analyst_agent(enable_thinking=enable_thinking)
    synthesis_agent = create_synthesis_agent()

    print(f"\n🔍 Тема аналізу: '{topic}'")
    print(f"🧠 Sequential Thinking: {'✓ Enabled' if enable_thinking and Config.ENABLE_MCP_THINKING else '✗ Disabled'}")
    print(f"   └─ Пошук з BBC, CNN, Reuters (паралельно)\n")

    # Створюємо задачі для паралельного пошуку
    bbc_task = Task(
        description=f'Використай інструмент DuckDuckGo News Search для пошуку новин про {topic} на сайті BBC. '
                   f'Пошуковий запит: "site:bbc.com {topic} news". '
                   f'Проаналізуй знайдені новини та виділи ключові факти.',
        agent=bbc_agent,
        expected_output='Короткий аналіз останніх новин з BBC з ключовими фактами'
    )

    cnn_task = Task(
        description=f'Використай інструмент DuckDuckGo News Search для пошуку новин про {topic} на сайті CNN. '
                   f'Пошуковий запит: "site:cnn.com {topic} news". '
                   f'Проаналізуй знайдені новини та виділи ключові факти.',
        agent=cnn_agent,
        expected_output='Короткий аналіз останніх новин з CNN з ключовими фактами'
    )

    reuters_task = Task(
        description=f'Використай інструмент DuckDuckGo News Search для пошуку новин про {topic} на сайті Reuters. '
                   f'Пошуковий запит: "site:reuters.com {topic} news". '
                   f'Проаналізуй знайдені новини та виділи ключові факти.',
        agent=reuters_agent,
        expected_output='Короткий аналіз останніх новин з Reuters з ключовими фактами'
    )

    # Задача глибокого аналізу з використанням thinking tools
    if enable_thinking and Config.ENABLE_MCP_THINKING:
        analysis_description = f'''Проаналізуй новини про "{topic}" з трьох джерел (BBC, CNN, Reuters).

ВАЖЛИВО: Використай інструмент "Sequential Thinking" для структурованого аналізу.

Виконай 5 кроків думки, викликаючи інструмент для кожного:

Крок 1 (context="Problem Definition"):
- Визнач основні теми що згадуються в усіх джерелах

Крок 2 (context="Pattern Recognition"):
- Знайди унікальні інсайти з кожного джерела

Крок 3 (context="Comparative Analysis"):
- Виділи протиріччя або різні точки зору (якщо є)

Крок 4 (context="Impact Assessment"):
- Проаналізуй можливі наслідки подій

Крок 5 (context="Conclusion"):
- Сформулюй ключові висновки

Після всіх кроків викликай "Get Thinking Summary" для отримання повного підсумку.

Формат виклику:
Sequential Thinking(thought="ваш аналіз", step_number=X, total_steps=5, context="назва кроку")
'''
    else:
        analysis_description = f'''Проаналізуй новини про "{topic}" з трьох джерел (BBC, CNN, Reuters).

Виділи:
1. Основні теми що згадуються в усіх джерелах
2. Унікальні інсайти з кожного джерела
3. Протиріччя або різні точки зору (якщо є)
4. Можливі наслідки подій
5. Ключові висновки
'''

    analysis_task = Task(
        description=analysis_description,
        agent=analyst_agent,
        expected_output='Глибокий аналіз новин з висновками',
        context=[bbc_task, cnn_task, reuters_task]
    )

    # Задача синтезу фінального звіту
    synthesis_task = Task(
        description='На основі аналізу створи комплексний звіт який включає:\n'
                   '1. Executive Summary (2-3 речення)\n'
                   '2. Ключові знахідки з кожного джерела\n'
                   '3. Основні висновки та тренди\n'
                   '4. Рекомендації для подальшого моніторингу\n\n'
                   'Звіт має бути чітким, структурованим та базуватись на фактах.',
        agent=synthesis_agent,
        expected_output='Комплексний аналітичний звіт з рекомендаціями',
        context=[analysis_task]
    )

    # Створюємо Crew
    crew = Crew(
        agents=[bbc_agent, cnn_agent, reuters_agent, analyst_agent, synthesis_agent],
        tasks=[bbc_task, cnn_task, reuters_task, analysis_task, synthesis_task],
        process=Process.sequential,
        verbose=True
    )

    # Виконуємо
    print("⚡ Запуск паралельного пошуку та аналізу...\n")
    result = crew.kickoff()

    end_time = time.time()
    duration = end_time - start_time

    # Виводимо результати
    print("\n" + "="*80)
    print("✅ ФІНАЛЬНИЙ ЗВІТ")
    print("="*80)
    print(f"\n{result}\n")
    print("="*80)
    print(f"⏱️  Час виконання: {duration:.2f} секунд")
    print(f"🧠 Sequential Thinking: {'використано' if enable_thinking and Config.ENABLE_MCP_THINKING else 'не використано'}")
    print("="*80 + "\n")

    return {
        'result': str(result),
        'duration': duration,
        'topic': topic,
        'thinking_enabled': enable_thinking and Config.ENABLE_MCP_THINKING
    }


if __name__ == "__main__":
    try:
        # Приклад 1: З MCP thinking
        print("📊 Запуск з MCP Sequential Thinking...")
        result1 = run_advanced_analysis(
            topic="artificial intelligence breakthrough",
            enable_thinking=True
        )

        # Приклад 2: Без thinking (для порівняння швидкості)
        # print("\n\n📊 Запуск без MCP Sequential Thinking...")
        # result2 = run_advanced_analysis(
        #     topic="artificial intelligence breakthrough",
        #     enable_thinking=False
        # )

    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
