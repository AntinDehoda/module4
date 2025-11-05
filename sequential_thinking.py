"""
Sequential Thinking для CrewAI
Простий але ефективний інструмент для структурованого мислення
"""

from crewai.tools import tool
from typing import Optional, List, Dict, Any
import json
from datetime import datetime


class ThinkingStep:
    """Один крок структурованого мислення"""

    def __init__(
        self,
        thought: str,
        step_number: int,
        total_steps: int,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.thought = thought
        self.step_number = step_number
        self.total_steps = total_steps
        self.timestamp = timestamp or datetime.now().isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thought": self.thought,
            "step_number": self.step_number,
            "total_steps": self.total_steps,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class SequentialThinkingProcess:
    """Процес структурованого мислення"""

    def __init__(self):
        self.steps: List[ThinkingStep] = []
        self.current_step = 0

    def add_step(
        self,
        thought: str,
        step_number: int,
        total_steps: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ThinkingStep:
        """Додає крок мислення"""
        step = ThinkingStep(
            thought=thought,
            step_number=step_number,
            total_steps=total_steps,
            metadata=metadata
        )
        self.steps.append(step)
        self.current_step = len(self.steps)
        return step

    def get_step(self, step_number: int) -> Optional[ThinkingStep]:
        """Отримує крок за номером"""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None

    def get_summary(self) -> str:
        """Генерує підсумок процесу мислення"""
        if not self.steps:
            return "Процес мислення порожній."

        summary_lines = [
            f"\n{'='*70}",
            f"📊 СТРУКТУРОВАНИЙ ПРОЦЕС МИСЛЕННЯ ({len(self.steps)} кроків)",
            f"{'='*70}\n"
        ]

        for step in self.steps:
            summary_lines.append(f"Крок {step.step_number}/{step.total_steps}:")
            summary_lines.append(f"  💭 {step.thought}")

            if step.metadata:
                for key, value in step.metadata.items():
                    summary_lines.append(f"  └─ {key}: {value}")

            summary_lines.append("")

        summary_lines.append(f"{'='*70}\n")
        return "\n".join(summary_lines)

    def reset(self):
        """Скидає процес мислення"""
        self.steps = []
        self.current_step = 0


# Глобальний процес мислення
_thinking_process = SequentialThinkingProcess()


@tool("Sequential Thinking")
def think_step(
    thought: str,
    step_number: int,
    total_steps: int = 5,
    context: Optional[str] = None
) -> str:
    """
    Інструмент для структурованого покрокового мислення.

    Використовуйте цей інструмент для розбиття складних проблем на логічні кроки.

    Args:
        thought: Ваша думка/аналіз для цього кроку
        step_number: Номер поточного кроку (1, 2, 3, ...)
        total_steps: Загальна кількість кроків (за замовчуванням 5)
        context: Додатковий контекст або категорія кроку

    Returns:
        Підтвердження запису та статус прогресу

    Example:
        # Крок 1
        think_step(
            thought="Визначаю основну проблему: потрібно проаналізувати дані з 3 джерел",
            step_number=1,
            total_steps=5,
            context="Problem Definition"
        )

        # Крок 2
        think_step(
            thought="Знаходжу спільні теми: всі джерела згадують AI та етику",
            step_number=2,
            total_steps=5,
            context="Pattern Recognition"
        )
    """
    metadata = {}
    if context:
        metadata["context"] = context

    step = _thinking_process.add_step(
        thought=thought,
        step_number=step_number,
        total_steps=total_steps,
        metadata=metadata
    )

    # Формуємо відповідь
    progress_bar = "█" * step_number + "░" * (total_steps - step_number)

    response_lines = [
        f"\n✓ Крок {step_number}/{total_steps} записано",
        f"[{progress_bar}] {int(step_number/total_steps*100)}%",
        f"\n💭 {thought[:100]}{'...' if len(thought) > 100 else ''}",
    ]

    if context:
        response_lines.append(f"📑 Контекст: {context}")

    if step_number == total_steps:
        response_lines.extend([
            f"\n{'─'*50}",
            "✅ Процес мислення завершено!",
            f"📊 Всього кроків: {len(_thinking_process.steps)}",
            f"{'─'*50}"
        ])
    else:
        response_lines.append(f"\n→ Переходимо до кроку {step_number + 1}")

    return "\n".join(response_lines)


@tool("Get Thinking Summary")
def get_thinking_summary() -> str:
    """
    Повертає повний підсумок процесу структурованого мислення.

    Використовуйте після завершення всіх кроків мислення для отримання
    повного огляду проведеного аналізу.

    Returns:
        Форматований підсумок всіх кроків мислення

    Example:
        # Після всіх кроків think_step
        summary = get_thinking_summary()
        print(summary)
    """
    return _thinking_process.get_summary()


@tool("Clear Thinking Process")
def clear_thinking() -> str:
    """
    Очищає поточний процес мислення.

    Використовуйте перед початком нового аналізу для очищення
    попередніх кроків.

    Returns:
        Підтвердження очищення
    """
    steps_count = len(_thinking_process.steps)
    _thinking_process.reset()
    return f"✓ Процес мислення очищено. Видалено {steps_count} кроків."


def reset_thinking_process():
    """Скидає глобальний процес мислення (для програмного використання)"""
    _thinking_process.reset()


# Експорт інструментів
THINKING_TOOLS = [
    think_step,
    get_thinking_summary,
    clear_thinking
]


if __name__ == "__main__":
    # Демонстрація
    print("🧪 Демонстрація Sequential Thinking\n")

    # Симуляція процесу мислення
    print(think_step.run(
        thought="Аналізуємо вхідні дані з трьох різних джерел новин",
        step_number=1,
        total_steps=5,
        context="Data Analysis"
    ))

    print(think_step.run(
        thought="Виявляємо спільні теми: AI, етика, регуляції",
        step_number=2,
        total_steps=5,
        context="Pattern Recognition"
    ))

    print(think_step.run(
        thought="Порівнюємо різні точки зору кожного джерела",
        step_number=3,
        total_steps=5,
        context="Comparative Analysis"
    ))

    print(think_step.run(
        thought="Аналізуємо можливі наслідки виявлених трендів",
        step_number=4,
        total_steps=5,
        context="Impact Assessment"
    ))

    print(think_step.run(
        thought="Формулюємо висновки та рекомендації на основі аналізу",
        step_number=5,
        total_steps=5,
        context="Conclusion"
    ))

    # Показуємо підсумок
    print(get_thinking_summary.run())

    print("\n✅ Демонстрація завершена!")
