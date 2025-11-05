"""
Advanced CrewAI Agent з паралельним запуском та MCP Sequential Thinking

Цей агент демонструє:
1. Паралельний пошук новин з 3 джерел (BBC, CNN, Reuters)
2. Офіційний MCP Sequential Thinking сервер для глибокого аналізу
3. Синтез висновків з рекомендаціями

Використовує вбудовану підтримку MCP через MCPServerAdapter.
"""

import time
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from duckduckgo_search import DDGS
from config import Config

# Initialize configuration
Config.validate()

print("🔌 Підготовка до підключення MCP Sequential Thinking сервера...")


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


def get_mcp_server_parameters():
    """Параметри для підключення до MCP Sequential Thinking сервера"""
    return StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-sequential-thinking"],
        env=None
    )


def create_analyst_agent_with_mcp(mcp_tools):
    """Створює агента-аналітика з MCP thinking tools

    Args:
        mcp_tools: Список MCP інструментів з MCPServerAdapter
    """
    analyst_agent = Agent(
        role='Senior News Analyst',
        goal='Провести глибокий аналіз новин з різних джерел та виробити висновки',
        backstory='Ти досвідчений аналітик новин з 15 років досвіду. '
                 'Ти використовуєш MCP Sequential Thinking для аналізу складних ситуацій. '
                 'Твої висновки завжди базуються на фактах та логічному аналізі.',
        tools=mcp_tools,
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


def run_advanced_analysis(topic="artificial intelligence"):
    """
    Запускає розширений аналіз новин з MCP thinking

    Args:
        topic: Тема для пошуку новин

    Returns:
        Dict з результатами аналізу
    """

    print("\n" + "="*80)
    print("🚀 ADVANCED CREWAI: Паралельний пошук + MCP Sequential Thinking")
    print("="*80 + "\n")

    # Створюємо агентів для пошуку
    print("📋 Створення пошукових агентів...")
    bbc_agent, cnn_agent, reuters_agent = create_search_agents()
    synthesis_agent = create_synthesis_agent()

    print(f"\n🔍 Тема аналізу: '{topic}'")
    print(f"🧠 MCP Sequential Thinking: Підключаємось...")
    print(f"   └─ Пошук з BBC, CNN, Reuters (паралельно)\n")

    # Підключаємось до MCP сервера через context manager
    server_params = get_mcp_server_parameters()

    try:
        with MCPServerAdapter(server_params, connect_timeout=60) as mcp_tools:
            print(f"✅ MCP сервер підключено! Доступно інструментів: {len(mcp_tools)}")

            # Показуємо доступні інструменти
            if mcp_tools:
                print(f"   📋 Інструменти:")
                for tool in mcp_tools:
                    print(f"      • {tool.name}")
            print()

            # Створюємо аналітика з MCP tools
            analyst_agent = create_analyst_agent_with_mcp(mcp_tools)

            start_time = time.time()

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

            # Задача глибокого аналізу з MCP Sequential Thinking
            analysis_description = f'''Проаналізуй новини про "{topic}" з трьох джерел (BBC, CNN, Reuters).

ВАЖЛИВО: Використай інструмент "sequentialthinking" (MCP Sequential Thinking) для структурованого аналізу.

Виконай 5 кроків думки, викликаючи MCP інструмент для кожного:

Крок 1 - thought: "Визначаю основні теми що згадуються в усіх джерелах: [твій аналіз]"
        thoughtNumber: 1, totalThoughts: 5, nextThoughtNeeded: true

Крок 2 - thought: "Знаходжу унікальні інсайти з кожного джерела: [твій аналіз]"
        thoughtNumber: 2, totalThoughts: 5, nextThoughtNeeded: true

Крок 3 - thought: "Виділяю протиріччя або різні точки зору: [твій аналіз]"
        thoughtNumber: 3, totalThoughts: 5, nextThoughtNeeded: true

Крок 4 - thought: "Аналізую можливі наслідки подій: [твій аналіз]"
        thoughtNumber: 4, totalThoughts: 5, nextThoughtNeeded: true

Крок 5 - thought: "Формулюю ключові висновки: [твій аналіз]"
        thoughtNumber: 5, totalThoughts: 5, nextThoughtNeeded: false

Кожний виклик інструменту sequentialthinking автоматично візуалізується MCP сервером.
'''

            analysis_task = Task(
                description=analysis_description,
                agent=analyst_agent,
                expected_output='Глибокий аналіз новин з висновками використовуючи MCP Sequential Thinking',
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
            print(f"🧠 MCP Sequential Thinking: використано")
            print("="*80 + "\n")

            return {
                'result': str(result),
                'duration': duration,
                'topic': topic,
                'mcp_enabled': True
            }

    except Exception as e:
        print(f"\n❌ Помилка підключення до MCP: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    try:
        # Запуск з MCP Sequential Thinking
        print("📊 Запуск з MCP Sequential Thinking...\n")
        result = run_advanced_analysis(
            topic="artificial intelligence breakthrough"
        )

        print("\n✅ Аналіз завершено успішно!")
        print(f"📄 Час виконання: {result['duration']:.2f}с")

    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
