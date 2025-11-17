"""
Memory Agent Module - Knowledge Graph Management with MCP Memory Server

This module provides functionality for managing knowledge graphs using the
MCP Memory server. It creates entities and relationships from news analysis.

New Structure:
- Source entities (BBC News, CNN News, Reuters News) with search URLs
- Topic entity with analysis results
- Relations: topic -> sources (analyzed_in)
"""

from crewai import Agent, Task
from mcp import StdioServerParameters


def get_mcp_memory_server_parameters():
    """
    Get parameters for connecting to MCP Memory server

    Returns:
        StdioServerParameters: Configuration for npx-based MCP Memory server
    """
    return StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-memory"],
        env=None
    )


def create_knowledge_agent(memory_tools):
    """
    Create Knowledge Manager agent with MCP Memory tools

    The agent is responsible for:
    - Creating source entities (BBC News, CNN News, Reuters News) with search URLs
    - Creating topic entity with analysis results
    - Creating relationships between topics and sources
    - Building persistent knowledge over time

    Args:
        memory_tools: List of MCP Memory tools from MCPServerAdapter

    Returns:
        Agent: CrewAI agent configured with memory tools
    """
    knowledge_agent = Agent(
        role='Knowledge Manager',
        goal='Зберігати та керувати знаннями через knowledge graph',
        backstory='Ти експерт з організації знань та створення зв\'язків між концепціями.',
        tools=memory_tools,
        verbose=True,
        allow_delegation=False
    )

    return knowledge_agent


def create_knowledge_task(knowledge_agent, search_tasks, analysis_task, topic):
    """
    Create task for building knowledge graph from search results and analysis

    This task:
    1. Extracts URLs from search task outputs (BBC, CNN, Reuters)
    2. Creates 3 source entities with URLs as observations
    3. Creates 1 topic entity with analysis output as observations
    4. Creates 3 relations: topic -> sources (analyzed_in)

    Args:
        knowledge_agent: Agent with memory tools
        search_tasks: List of completed search tasks [bbc_task, cnn_task, reuters_task]
        analysis_task: Completed analysis task with Sequential Thinking output
        topic: The topic being analyzed (string)

    Returns:
        Task: CrewAI task for knowledge graph creation
    """

    knowledge_description = f'''
Використай MCP Memory інструменти для створення knowledge graph з результатів пошуку та аналізу.

На основі результатів з BBC, CNN, Reuters та аналізу:

1. Створи сутності (entities) для кожного джерела новин:
   - create_entities: name="BBC News", entityType="source", observations=[список URLs з BBC результатів]
   - create_entities: name="CNN News", entityType="source", observations=[список URLs з CNN результатів]
   - create_entities: name="Reuters News", entityType="source", observations=[список URLs з Reuters результатів]

   ВАЖЛИВО: Витягни URLs з результатів пошуку. Якщо URLs не знайдено, використай ["No URLs found"].

2. Створи сутність для теми аналізу:
   - create_entities: name="{topic}", entityType="topic", observations=[повний текст аналізу з analysis_task]

   ВАЖЛИВО: Observations має містити повний результат аналізу від Senior News Analyst.

3. Створи зв'язки (relations) від теми до кожного джерела:
   - create_relations: from="{topic}", to="BBC News", relationType="analyzed_in"
   - create_relations: from="{topic}", to="CNN News", relationType="analyzed_in"
   - create_relations: from="{topic}", to="Reuters News", relationType="analyzed_in"

Після створення всіх сутностей та зв'язків, поверни звіт у форматі:

```
KNOWLEDGE GRAPH SUMMARY
=======================

Created Entities:
- Sources: 3 (BBC News, CNN News, Reuters News)
- Topic: "{topic}"

Created Relations:
- analyzed_in relations: 3 (topic → each source)

Total: 4 entities, 3 relations

URLs Saved:
- BBC: [кількість URLs]
- CNN: [кількість URLs]
- Reuters: [кількість URLs]
```

ВАЖЛИВО:
- Всі назви entities англійською мовою для консистентності
- URLs з результатів пошуку обов'язково зберегти
- Повний аналіз з analysis_task зберегти як observations для topic entity
'''

    knowledge_task = Task(
        description=knowledge_description,
        agent=knowledge_agent,
        expected_output='Структурований звіт про створений knowledge graph з кількістю entities та relations',
        context=[*search_tasks, analysis_task]  # Include all search tasks and analysis
    )

    return knowledge_task


def get_analysis_history(knowledge_agent, topic):
    """
    Create task for querying previous analyses of the same topic from knowledge graph

    This task queries the memory for historical analyses:
    1. Searches for the topic entity by name
    2. Retrieves all related source entities
    3. Gets observations (previous analysis results)
    4. Returns formatted history

    Args:
        knowledge_agent: Agent with memory tools
        topic: The topic to search for (string)

    Returns:
        Task: CrewAI task for querying analysis history
    """

    history_description = f'''
Використай MCP Memory інструменти для пошуку попередніх аналізів теми "{topic}".

Виконай наступні кроки:

1. Використай інструмент search_nodes для пошуку topic entity з назвою "{topic}":
   - search_nodes: query="{topic}"

2. Якщо знайдено topic entity:
   - Отримай всі observations (це попередні аналізи)
   - Знайди всі зв'язані source entities через relations
   - Отримай observations з sources (URLs попередніх пошуків)

3. Якщо topic НЕ знайдено:
   - Поверни повідомлення що це перший аналіз цієї теми

Поверни результат у форматі:

```
ANALYSIS HISTORY FOR: {topic}
================================

Previous Analyses Found: [кількість або "None - first analysis"]

{{Якщо знайдено попередні аналізи:}}

Historical Analysis:
-------------------
[Повний текст попереднього аналізу з observations]

Sources Used Previously:
- BBC News: [URLs]
- CNN News: [URLs]
- Reuters News: [URLs]

Summary:
--------
[Короткий висновок про те що вже було проаналізовано раніше]

{{Якщо НЕ знайдено:}}

This is the first analysis of "{topic}". No historical data available.
```

ВАЖЛИВО:
- Якщо знайдено декілька topic entities, використай найновішу
- Observations містять повні тексти попередніх аналізів
- Ця інформація допоможе synthesis agent побачити динаміку змін
'''

    history_task = Task(
        description=history_description,
        agent=knowledge_agent,
        expected_output=f'Історія попередніх аналізів теми {topic} або повідомлення що це перший аналіз',
        context=[]  # No dependencies - queries existing knowledge
    )

    return history_task


# Utility functions

def get_memory_tools_info(memory_tools):
    """
    Get information about available memory tools

    Args:
        memory_tools: List of MCP Memory tools

    Returns:
        list: List of tool names and descriptions
    """
    tools_info = []
    for tool in memory_tools:
        tools_info.append({
            'name': tool.name,
            'description': getattr(tool, 'description', 'No description available')
        })
    return tools_info


if __name__ == "__main__":
    # Example usage and testing
    print("=" * 80)
    print("Memory Agent Module - Knowledge Graph Management")
    print("=" * 80)
    print()

    print("New Knowledge Graph Structure:")
    print()

    print("Entities:")
    print("  • Source entities: BBC News, CNN News, Reuters News")
    print("    - Type: 'source'")
    print("    - Observations: URLs from search results")
    print()
    print("  • Topic entity: [topic name, e.g. 'artificial intelligence']")
    print("    - Type: 'topic'")
    print("    - Observations: Full analysis output from analyst")
    print()

    print("Relations:")
    print("  • analyzed_in: topic → source")
    print("    - Connects topic to each source used in analysis")
    print("    - Example: 'artificial intelligence' → 'BBC News'")
    print()

    print("Functions:")
    print("  • create_knowledge_task() - Saves current analysis to knowledge graph")
    print("  • get_analysis_history() - Retrieves previous analyses of same topic")
    print()

    print("MCP Memory Server Configuration:")
    params = get_mcp_memory_server_parameters()
    print(f"  Command: {params.command}")
    print(f"  Args: {' '.join(params.args)}")
    print()

    print("✅ Memory Agent module loaded successfully!")
    print()
    print("Import this module in your main script:")
    print("  from memory_agent import create_knowledge_agent, create_knowledge_task, get_analysis_history")
