"""
Advanced CrewAI Agent з паралельним запуском, MCP Sequential Thinking та Memory

Цей агент демонструє:
1. Паралельний пошук новин з 3 джерел (BBC, CNN, Reuters)
2. Офіційний MCP Sequential Thinking сервер для глибокого аналізу
3. MCP Memory сервер для зберігання знань у knowledge graph
4. Синтез висновків з рекомендаціями

Використовує вбудовану підтримку MCP через MCPServerAdapter.
"""

import time
import requests
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from config import Config
from ddgs import DDGS

# Import memory agent module
from memory_agent import (
    get_mcp_memory_server_parameters,
    create_knowledge_agent,
    create_knowledge_task,
    get_analysis_history
)

# Initialize configuration
Config.validate()

print("🔌 Підготовка до підключення MCP серверів...")


@tool("DDGS News Search")
def search_news(query: str) -> str:
    """
    Пошук новин через DDGS Search API.

    Args:
        query: Пошуковий запит

    Returns:
        Результати пошуку новин
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                output = ""
                for i, r in enumerate(results, 1):
                    output += f"{i}. {r.get('title', '')}\n"
                    output += f"   {r.get('body', '')[:200]}...\n"
                    output += f"   {r.get('href', '')}\n\n"
                return output
            return f"Новин не знайдено для запиту: {query}"
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


def get_mcp_thinking_server_parameters():
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


def run_advanced_analysis_with_memory(topic="artificial intelligence"):
    """
    Запускає розширений аналіз новин з MCP thinking та memory

    Args:
        topic: Тема для пошуку новин

    Returns:
        Dict з результатами аналізу
    """

    print("\n" + "="*80)
    print("🚀 ADVANCED CREWAI: Пошук + MCP Sequential Thinking + Memory")
    print("="*80 + "\n")

    # Створюємо агентів для пошуку
    print("📋 Створення пошукових агентів...")
    bbc_agent, cnn_agent, reuters_agent = create_search_agents()
    synthesis_agent = create_synthesis_agent()

    print(f"\n🔍 Тема аналізу: '{topic}'")
    print(f"🧠 MCP Sequential Thinking: Підключаємось...")
    print(f"💾 MCP Memory: Підключаємось...")
    print(f"   └─ Пошук з BBC, CNN, Reuters (паралельно)\n")

    # Підключаємось до обох MCP серверів
    thinking_params = get_mcp_thinking_server_parameters()
    memory_params = get_mcp_memory_server_parameters()

    try:
        # Context manager для Sequential Thinking
        with MCPServerAdapter(thinking_params, connect_timeout=60) as thinking_tools:
            print(f"✅ MCP Sequential Thinking підключено! Інструментів: {len(thinking_tools)}")
            if thinking_tools:
                print(f"   📋 Thinking інструменти:")
                for tool in thinking_tools:
                    print(f"      • {tool.name}")

            # Context manager для Memory
            with MCPServerAdapter(memory_params, connect_timeout=60) as memory_tools:
                print(f"✅ MCP Memory підключено! Інструментів: {len(memory_tools)}")
                if memory_tools:
                    print(f"   💾 Memory інструменти:")
                    for tool in memory_tools:
                        print(f"      • {tool.name}")
                print()

                # Створюємо агентів з MCP tools
                analyst_agent = create_analyst_agent_with_mcp(thinking_tools)
                knowledge_agent = create_knowledge_agent(memory_tools)

                start_time = time.time()

                # Створюємо задачі для паралельного пошуку
                bbc_task = Task(
                    description=f'Використай інструмент DDGS News Search для пошуку новин про {topic} на сайті BBC. '
                               f'Пошуковий запит: "site:bbc.com {topic} news". '
                               f'Проаналізуй знайдені новини та виділи ключові факти у форматі:\n'
                               f'ДЖЕРЕЛО: BBC\n'
                               f'ТЕМИ: [список основних тем через кому]\n'
                               f'КЛЮЧОВІ ФАКТИ: [список фактів]\n',
                    agent=bbc_agent,
                    expected_output='Структурований аналіз новин з BBC з джерелом, темами та фактами'
                )

                cnn_task = Task(
                    description=f'Використай інструмент DDGS News Search для пошуку новин про {topic} на сайті CNN. '
                               f'Пошуковий запит: "site:cnn.com {topic} news". '
                               f'Проаналізуй знайдені новини та виділи ключові факти у форматі:\n'
                               f'ДЖЕРЕЛО: CNN\n'
                               f'ТЕМИ: [список основних тем через кому]\n'
                               f'КЛЮЧОВІ ФАКТИ: [список фактів]\n',
                    agent=cnn_agent,
                    expected_output='Структурований аналіз новин з CNN з джерелом, темами та фактами'
                )

                reuters_task = Task(
                    description=f'Використай інструмент DDGS News Search для пошуку новин про {topic} на сайті Reuters. '
                               f'Пошуковий запит: "site:reuters.com {topic} news". '
                               f'Проаналізуй знайдені новини та виділи ключові факти у форматі:\n'
                               f'ДЖЕРЕЛО: Reuters\n'
                               f'ТЕМИ: [список основних тем через кому]\n'
                               f'КЛЮЧОВІ ФАКТИ: [список фактів]\n',
                    agent=reuters_agent,
                    expected_output='Структурований аналіз новин з Reuters з джерелом, темами та фактами'
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

                # Задача пошуку історії попередніх аналізів
                history_task = get_analysis_history(
                    knowledge_agent=knowledge_agent,
                    topic=topic
                )

                # Задача для створення knowledge graph з результатів пошуку та аналізу
                knowledge_task = create_knowledge_task(
                    knowledge_agent=knowledge_agent,
                    search_tasks=[bbc_task, cnn_task, reuters_task],
                    analysis_task=analysis_task,
                    topic=topic
                )

                # Задача синтезу фінального звіту
                synthesis_task = Task(
                    description='На основі поточного аналізу, історичних даних та knowledge graph створи комплексний звіт який включає:\n'
                               '1. Executive Summary (2-3 речення)\n'
                               '2. Ключові знахідки з кожного джерела (BBC, CNN, Reuters)\n'
                               '3. Основні висновки та тренди\n'
                               '4. Порівняння з попередніми аналізами (якщо доступні з history)\n'
                               '5. Динаміка змін (що змінилось з моменту попереднього аналізу)\n'
                               '6. Knowledge Graph Summary (скільки створено сутностей та зв\'язків)\n'
                               '7. Рекомендації для подальшого моніторингу\n\n'
                               'ВАЖЛИВО: Використай історичний контекст з history task для виявлення трендів та змін.\n'
                               'Звіт має бути чітким, структурованим та базуватись на фактах.',
                    agent=synthesis_agent,
                    expected_output='Комплексний аналітичний звіт з історичним контекстом, рекомендаціями та knowledge graph summary',
                    context=[analysis_task, knowledge_task, history_task]
                )

                # Створюємо Crew
                crew = Crew(
                    agents=[bbc_agent, cnn_agent, reuters_agent, analyst_agent, knowledge_agent, synthesis_agent],
                    tasks=[bbc_task, cnn_task, reuters_task, analysis_task, history_task, knowledge_task, synthesis_task],
                    process=Process.sequential,
                    verbose=True
                )

                # Виконуємо
                print("⚡ Запуск паралельного пошуку, аналізу та збереження знань...\n")
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
                print(f"💾 MCP Memory: knowledge graph створено")
                print(f"📜 History: попередні аналізи завантажено")
                print("="*80 + "\n")

                # Доступ до індивідуальних результатів задач
                print("📊 Індивідуальні результати задач:")
                print(f"\n📰 BBC Task Output:\n{bbc_task.output}\n")
                print(f"\n📰 CNN Task Output:\n{cnn_task.output}\n")
                print(f"\n📰 Reuters Task Output:\n{reuters_task.output}\n")
                print(f"\n🧠 Analysis Task Output:\n{analysis_task.output}\n")
                print(f"\n📜 History Task Output:\n{history_task.output}\n")
                print(f"\n💾 Knowledge Graph Task Output:\n{knowledge_task.output}\n")

                return {
                    'result': str(result),
                    'duration': duration,
                    'topic': topic,
                    'mcp_enabled': True,
                    'memory_enabled': True,
                    'bbc_output': str(bbc_task.output),
                    'cnn_output': str(cnn_task.output),
                    'reuters_output': str(reuters_task.output),
                    'analysis_output': str(analysis_task.output),
                    'history_output': str(history_task.output),
                    'knowledge_output': str(knowledge_task.output)
                }

    except Exception as e:
        print(f"\n❌ Помилка підключення до MCP: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    try:
        # Запуск з MCP Sequential Thinking та Memory
        print("📊 Запуск з MCP Sequential Thinking + Memory...\n")
        result = run_advanced_analysis_with_memory(
            topic="artificial intelligence breakthrough"
        )

        print("\n✅ Аналіз завершено успішно!")
        print(f"📄 Час виконання: {result['duration']:.2f}с")
        print(f"💾 Knowledge Graph: створено та збережено")
        print(f"📜 History: попередні аналізи опрацьовано")

    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
