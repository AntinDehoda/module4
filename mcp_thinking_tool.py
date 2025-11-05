"""
MCP Sequential Thinking Tool Wrapper for CrewAI

Цей модуль створює CrewAI-сумісний інструмент для MCP sequential-thinking.
"""

from crewai.tools import tool
from typing import Dict, Any, Optional
import json


class ThinkingProcess:
    """Клас для збереження процесу мислення"""

    def __init__(self):
        self.thoughts = []
        self.current_thought = 0
        self.branches = []

    def add_thought(self, thought_data: Dict[str, Any]):
        """Додає крок мислення"""
        self.thoughts.append(thought_data)
        self.current_thought = len(self.thoughts)

    def get_summary(self) -> str:
        """Повертає підсумок процесу мислення"""
        if not self.thoughts:
            return "Процес мислення ще не почався."

        summary = f"Процес мислення ({len(self.thoughts)} кроків):\n\n"

        for i, thought in enumerate(self.thoughts, 1):
            summary += f"Крок {i}/{len(self.thoughts)}:\n"
            summary += f"  {thought.get('thought', 'N/A')}\n"

            if thought.get('isRevision'):
                summary += f"  [Переопрацювання кроку {thought.get('revisesThought')}]\n"

            if thought.get('branchId'):
                summary += f"  [Гілка: {thought.get('branchId')}]\n"

            summary += "\n"

        return summary


# Глобальний екземпляр для збереження процесу мислення
_thinking_process = ThinkingProcess()


@tool("Sequential Thinking")
def sequential_thinking(
    thought: str,
    thought_number: int = 1,
    total_thoughts: int = 5,
    next_thought_needed: bool = True,
    is_revision: bool = False,
    revises_thought: Optional[int] = None,
    branch_from_thought: Optional[int] = None,
    branch_id: Optional[str] = None,
    needs_more_thoughts: bool = False
) -> str:
    """
    Інструмент для структурованого покрокового мислення.

    Дозволяє розбивати складні проблеми на послідовні кроки з можливістю
    переопрацювання, галуження та динамічного коригування.

    Args:
        thought: Поточний крок мислення
        thought_number: Номер поточної думки (починаючи з 1)
        total_thoughts: Очікувана загальна кількість кроків
        next_thought_needed: Чи потрібний наступний крок
        is_revision: Чи це переопрацювання попереднього кроку
        revises_thought: Номер кроку для переопрацювання (якщо is_revision=True)
        branch_from_thought: Номер кроку від якого відгалужуємось
        branch_id: Ідентифікатор гілки
        needs_more_thoughts: Чи потрібні додаткові кроки понад total_thoughts

    Returns:
        Підтвердження запису думки та поточний статус
    """

    # Зберігаємо крок мислення
    thought_data = {
        "thought": thought,
        "thoughtNumber": thought_number,
        "totalThoughts": total_thoughts,
        "nextThoughtNeeded": next_thought_needed,
        "isRevision": is_revision,
        "revisesThought": revises_thought,
        "branchFromThought": branch_from_thought,
        "branchId": branch_id,
        "needsMoreThoughts": needs_more_thoughts
    }

    _thinking_process.add_thought(thought_data)

    # Формуємо відповідь
    response = f"✓ Крок {thought_number}/{total_thoughts} записано\n"
    response += f"Думка: {thought[:100]}{'...' if len(thought) > 100 else ''}\n"

    if is_revision:
        response += f"[Переопрацювання кроку {revises_thought}]\n"

    if not next_thought_needed:
        response += "\n✅ Процес мислення завершено!\n"
        response += f"Всього кроків: {len(_thinking_process.thoughts)}\n"
    else:
        response += f"→ Продовжуємо до кроку {thought_number + 1}\n"

    return response


@tool("Get Thinking Summary")
def get_thinking_summary() -> str:
    """
    Повертає повний підсумок процесу мислення.

    Корисно для перегляду всіх кроків мислення які були зроблені.

    Returns:
        Форматований підсумок всіх кроків мислення
    """
    return _thinking_process.get_summary()


def reset_thinking_process():
    """Скидає процес мислення (корисно для нових задач)"""
    global _thinking_process
    _thinking_process = ThinkingProcess()


# Список інструментів для експорту
THINKING_TOOLS = [
    sequential_thinking,
    get_thinking_summary
]


if __name__ == "__main__":
    # Тест інструментів
    print("Тестування MCP Thinking Tools...\n")

    # Тест послідовного мислення
    result1 = sequential_thinking.run(
        thought="Спочатку потрібно проаналізувати вхідні дані",
        thought_number=1,
        total_thoughts=3,
        next_thought_needed=True
    )
    print(result1)
    print()

    result2 = sequential_thinking.run(
        thought="Виявлено три основні тренди в даних",
        thought_number=2,
        total_thoughts=3,
        next_thought_needed=True
    )
    print(result2)
    print()

    result3 = sequential_thinking.run(
        thought="Висновок: потрібно зосередитись на тренді A",
        thought_number=3,
        total_thoughts=3,
        next_thought_needed=False
    )
    print(result3)
    print()

    # Тест підсумку
    summary = get_thinking_summary.run()
    print(summary)

    print("✅ Тести пройдені успішно!")
