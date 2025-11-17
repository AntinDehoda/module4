# Memory MCP Server Integration Guide

This document explains how to use the `parallel_agent_with_mcp_memory.py` which integrates MCP Memory server for building a knowledge graph with historical analysis tracking.

## 🎯 What's New

The implementation adds:

1. **MCP Memory Server Integration** - Persistent knowledge graph storage
2. **Knowledge Manager Agent** - Dedicated agent for managing knowledge
3. **Historical Analysis Tracking** - Queries previous analyses of the same topic
4. **Source Entity Tracking** - Stores URLs from news searches
5. **Topic Analysis Storage** - Saves full analysis results with timestamps
6. **Automatic Relationship Mapping** - Connects topics to sources

## 📊 Architecture

```
┌─────────────────┐
│ BBC Researcher  │─┐
└─────────────────┘ │
                    ├──► ┌──────────────────┐
┌─────────────────┐ │    │ Senior Analyst   │       ┌─────────────────┐
│ CNN Researcher  │─┤    │ (with Sequential │◄──────┤ MCP Sequential  │
└─────────────────┘ │    │  Thinking)       │       │ Thinking Server │
                    │    └──────────────────┘       └─────────────────┘
┌─────────────────┐ │              │
│Reuters Researcher│─┘              │
└─────────────────┘                 ▼
                          ┌──────────────────┐       ┌─────────────────┐
                          │ Knowledge Manager│◄──────┤ MCP Memory      │
                          │ (queries history │       │ Server          │
                          │  & saves new)    │       └─────────────────┘
                          └──────────────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │ Report Synthesizer│
                          │ (with historical  │
                          │  context)         │
                          └──────────────────┘
```

## 🔑 Key Features

### 1. New Knowledge Graph Structure

**Entities:**
- **Source entities**: `"BBC News"`, `"CNN News"`, `"Reuters News"`
  - Type: `"source"`
  - Observations: List of URLs from search results

- **Topic entity**: Topic name (e.g., `"artificial intelligence breakthrough"`)
  - Type: `"topic"`
  - Observations: Full analysis output from Sequential Thinking

**Relations:**
- **analyzed_in**: Connects topic to each source
  - Direction: `topic → source`
  - Example: `"artificial intelligence" → "BBC News"`

### 2. Historical Analysis Tracking

The system now queries previous analyses before creating new ones:

```python
# Query previous analyses
history_task = get_analysis_history(knowledge_agent, topic)

# Save current analysis
knowledge_task = create_knowledge_task(
    knowledge_agent=knowledge_agent,
    search_tasks=[bbc_task, cnn_task, reuters_task],
    analysis_task=analysis_task,
    topic=topic
)

# Synthesize with historical context
synthesis_task = Task(
    ...
    context=[analysis_task, knowledge_task, history_task]
)
```

### 3. Task Execution Order

The new workflow executes tasks in this order:

1. **Search tasks** (BBC, CNN, Reuters) - Parallel news searches
2. **Analysis task** - Sequential Thinking analysis of search results
3. **History task** - Query previous analyses from memory
4. **Knowledge task** - Save current analysis to memory
5. **Synthesis task** - Create final report with historical context

## 🚀 Usage

### Run with Docker

```bash
docker-compose run --rm crewai-mcp python parallel_agent_with_mcp_memory.py
```

### Run Locally

```bash
python parallel_agent_with_mcp_memory.py
```

### Programmatic Usage

```python
from parallel_agent_with_mcp_memory import run_advanced_analysis_with_memory

result = run_advanced_analysis_with_memory(
    topic="quantum computing breakthrough"
)

# Access all outputs
print("BBC findings:", result['bbc_output'])
print("CNN findings:", result['cnn_output'])
print("Reuters findings:", result['reuters_output'])
print("Analysis:", result['analysis_output'])
print("History:", result['history_output'])
print("Knowledge graph:", result['knowledge_output'])
```

## 📝 Knowledge Graph Operations

### Creating Entities

The knowledge manager automatically creates:

```python
# Source entities with URLs
create_entities(
    name="BBC News",
    entityType="source",
    observations=["https://bbc.com/article1", "https://bbc.com/article2"]
)

# Topic entity with analysis
create_entities(
    name="artificial intelligence breakthrough",
    entityType="topic",
    observations=["Full analysis text from Sequential Thinking..."]
)
```

### Creating Relations

The system automatically connects topics to sources:

```python
create_relations(
    from="artificial intelligence breakthrough",
    to="BBC News",
    relationType="analyzed_in"
)
```

### Querying History

The history task searches for previous analyses:

```python
# First analysis
history_task.output = "This is the first analysis of this topic"

# Subsequent analyses
history_task.output = """
ANALYSIS HISTORY FOR: artificial intelligence breakthrough
================================

Previous Analyses Found: 2

Historical Analysis:
-------------------
[Previous analysis text from 2024-01-15]

Sources Used Previously:
- BBC News: [3 URLs]
- CNN News: [4 URLs]
- Reuters News: [2 URLs]

Summary:
--------
Previous analyses focused on regulatory concerns. Current analysis shows
shift towards breakthrough implementations.
"""
```

## 💾 Knowledge Persistence

The MCP Memory server stores the knowledge graph persistently across runs:

**First Run:**
- Creates: 3 sources + 1 topic = 4 entities
- Creates: 3 relations (topic → each source)
- History: "First analysis"

**Second Run (same topic):**
- History: Shows previous analysis
- Creates: 3 sources (updated observations) + 1 topic = 4 new entities
- Creates: 3 new relations
- Synthesis: Compares with previous analysis

**Third Run (different topic):**
- History: "First analysis" (new topic)
- Creates: New topic entity
- Links to same sources (sources are reused)

## 🔄 Complete Workflow Example

```python
# User runs analysis on "AI regulation"
result = run_advanced_analysis_with_memory(topic="AI regulation")

# Workflow execution:
# 1. BBC/CNN/Reuters search for "AI regulation" → URLs collected
# 2. Analyst uses Sequential Thinking → Creates 5-step analysis
# 3. Knowledge Manager queries history → "First analysis" or previous results
# 4. Knowledge Manager saves:
#    - 3 source entities with new URLs
#    - 1 topic entity with current analysis
#    - 3 relations connecting topic to sources
# 5. Synthesizer creates report comparing with history (if any)

# Next day, run again:
result = run_advanced_analysis_with_memory(topic="AI regulation")

# Workflow execution:
# 1-2. Same as before
# 3. History task finds previous analysis from yesterday
# 4. Saves new analysis alongside old one
# 5. Synthesizer identifies changes: "Yesterday focused on EU, today includes US policy"
```

## 📊 Example Output

```
================================================================================
🚀 ADVANCED CREWAI: Пошук + MCP Sequential Thinking + Memory
================================================================================

✅ MCP Sequential Thinking підключено! Інструментів: 1
✅ MCP Memory підключено! Інструментів: 3

⚡ Запуск паралельного пошуку, аналізу та збереження знань...

[Task execution logs...]

================================================================================
✅ ФІНАЛЬНИЙ ЗВІТ
================================================================================

Executive Summary: Analysis of AI breakthroughs reveals significant progress
compared to last month's analysis...

Ключові знахідки з кожного джерела:
- BBC: [New findings with URLs]
- CNN: [New findings with URLs]
- Reuters: [New findings with URLs]

Порівняння з попередніми аналізами:
Previous analysis (2024-01-15) showed regulatory concerns. Current analysis
shows implementation breakthroughs...

Динаміка змін:
- Shift from theoretical to practical applications
- Increased focus on ethical frameworks
- New regulatory developments in EU and US

Knowledge Graph Summary:
- Created 4 entities (3 sources, 1 topic)
- Created 3 relations (topic → sources)
- Total URLs saved: 12

Рекомендації для подальшого моніторингу:
[Recommendations based on trends...]

================================================================================
⏱️  Час виконання: 45.32 секунд
🧠 MCP Sequential Thinking: використано
💾 MCP Memory: knowledge graph створено
📜 History: попередні аналізи завантажено
================================================================================

📊 Індивідуальні результати задач:

📰 BBC Task Output:
[BBC search results with URLs]

📰 CNN Task Output:
[CNN search results with URLs]

📰 Reuters Task Output:
[Reuters search results with URLs]

🧠 Analysis Task Output:
[5-step Sequential Thinking analysis]

📜 History Task Output:
ANALYSIS HISTORY FOR: artificial intelligence breakthrough
================================
Previous Analyses Found: 1
[Historical analysis details]

💾 Knowledge Graph Task Output:
KNOWLEDGE GRAPH SUMMARY
=======================
Created Entities: 4
Created Relations: 3
URLs Saved: 12
```

## 🔧 Customization

### Change Topic

```python
result = run_advanced_analysis_with_memory(
    topic="quantum computing"  # Different topic
)
```

### Add Custom Entity Types

Modify `memory_agent.py` to add new entity types:

```python
# In create_knowledge_task description:
create_entities: name="Expert Name", entityType="expert", observations=[...]
```

### Change Relation Types

Modify the relation type in `memory_agent.py`:

```python
create_relations: from="topic", to="source", relationType="cited_in"
```

## 🐛 Troubleshooting

### Memory Server Not Starting

```bash
# Test manually
npx -y @modelcontextprotocol/server-memory

# Check Node.js version
node --version  # Should be 18+
```

### History Not Loading

- First run of a topic will show "First analysis"
- History only shows data from previous runs with same topic name
- Case-sensitive: "AI" ≠ "ai"

### Entities Not Persisting

The MCP Memory server stores data in memory by default. For persistent storage across server restarts, configure the memory server with a database backend (check MCP Memory server documentation).

### Knowledge Task Fails

- Ensure search tasks produce structured output with URLs
- Verify analysis_task completes successfully before knowledge_task
- Check that topic name doesn't contain special characters

## 📚 Next Steps

1. **Run multiple analyses** on the same topic to build historical context
2. **Query the knowledge graph** using history task
3. **Compare trends** across multiple runs
4. **Export knowledge** for external analysis
5. **Visualize relationships** between topics and sources

## 🔗 References

- [MCP Memory Server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
- [MCP Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
- [CrewAI MCP Integration](https://docs.crewai.com/en/mcp/overview)
- [memory_agent.py Documentation](./memory_agent.py)

## 📋 Module Structure

The implementation is split into modular components:

### memory_agent.py
- `get_mcp_memory_server_parameters()` - Memory server configuration
- `create_knowledge_agent(memory_tools)` - Creates Knowledge Manager agent
- `create_knowledge_task(...)` - Task for saving analysis to knowledge graph
- `get_analysis_history(...)` - Task for querying previous analyses
- `get_memory_tools_info(memory_tools)` - Utility for tool information

### parallel_agent_with_mcp_memory.py
- Imports from memory_agent module
- Creates 6-agent crew with search, analysis, knowledge, and synthesis agents
- Executes tasks in optimized order
- Displays comprehensive results with historical context
