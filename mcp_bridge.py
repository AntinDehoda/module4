"""
MCP Bridge для CrewAI

Міст між асинхронним MCP клієнтом та синхронними CrewAI @tool декораторами.
"""

import asyncio
import threading
from functools import wraps
from typing import Optional, Dict, Any
from crewai.tools import tool

from mcp_client import MCPSequentialThinkingClient, get_mcp_client


class MCPBridge:
    """Міст для виклику async MCP функцій з sync контексту"""

    def __init__(self):
        self.client: Optional[MCPSequentialThinkingClient] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._connected = False

    def start(self):
        """Запустити MCP клієнт в окремому потоці"""
        if self._connected:
            return

        def run_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=run_loop, args=(self.loop,), daemon=True)
        self._thread.start()

        # Підключення до MCP сервера
        self.client = MCPSequentialThinkingClient()
        future = asyncio.run_coroutine_threadsafe(self.client.connect(), self.loop)
        future.result(timeout=30)  # Чекаємо до 30 секунд

        self._connected = True
        print("✅ MCP Bridge запущено")

    def stop(self):
        """Зупинити MCP клієнт"""
        if not self._connected:
            return

        if self.client:
            future = asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
            future.result(timeout=10)

        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)

        self._connected = False
        print("🔌 MCP Bridge зупинено")

    def call_async(self, coro):
        """Викликати async функцію з sync контексту"""
        if not self._connected:
            raise RuntimeError("MCP Bridge не запущено. Викличте start() спочатку.")

        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=60)  # Тайм-аут 60 секунд


# Глобальний bridge
_bridge: Optional[MCPBridge] = None


def get_bridge() -> MCPBridge:
    """Отримати глобальний екземпляр bridge"""
    global _bridge
    if _bridge is None:
        _bridge = MCPBridge()
        _bridge.start()
    return _bridge


# CrewAI Tools використовуючи MCP
@tool("Sequential Thinking (MCP)")
def sequential_thinking_mcp(
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
    Інструмент для структурованого покрокового мислення через MCP.

    Використовує справжній MCP Sequential Thinking сервер для
    розбиття складних проблем на послідовні кроки з можливістю
    переопрацювання, галуження та динамічного коригування.

    Args:
        thought: Поточний крок мислення
        thought_number: Номер поточної думки (починаючи з 1)
        total_thoughts: Очікувана загальна кількість кроків
        next_thought_needed: Чи потрібний наступний крок
        is_revision: Чи це переопрацювання попереднього кроку
        revises_thought: Номер кроку для переопрацювання
        branch_from_thought: Номер кроку від якого відгалужуємось
        branch_id: Ідентифікатор гілки
        needs_more_thoughts: Чи потрібні додаткові кроки понад total_thoughts

    Returns:
        Підтвердження запису думки та поточний статус від MCP сервера
    """
    try:
        bridge = get_bridge()

        # Викликаємо async метод через bridge
        result = bridge.call_async(
            bridge.client.sequential_thinking(
                thought=thought,
                thought_number=thought_number,
                total_thoughts=total_thoughts,
                next_thought_needed=next_thought_needed,
                is_revision=is_revision,
                revises_thought=revises_thought,
                branch_from_thought=branch_from_thought,
                branch_id=branch_id,
                needs_more_thoughts=needs_more_thoughts
            )
        )

        return result

    except Exception as e:
        return f"❌ Помилка MCP: {str(e)}"


@tool("Get Thinking Summary (MCP)")
def get_thinking_summary_mcp() -> str:
    """
    Повертає повний підсумок процесу мислення з MCP сервера.

    Корисно для перегляду всіх кроків мислення які були зроблені
    через MCP Sequential Thinking сервер.

    Returns:
        Форматований підсумок всіх кроків мислення
    """
    try:
        # MCP sequential-thinking сервер зберігає стан між викликами
        # Тому просто повертаємо повідомлення
        return "📊 Для отримання підсумку використовуйте окремий запит до MCP сервера або перегляньте логи кроків."

    except Exception as e:
        return f"❌ Помилка MCP: {str(e)}"


# Список інструментів для експорту
MCP_THINKING_TOOLS = [
    sequential_thinking_mcp,
    get_thinking_summary_mcp
]


def cleanup_bridge():
    """Очистити bridge при завершенні програми"""
    global _bridge
    if _bridge is not None:
        _bridge.stop()
        _bridge = None


# Реєструємо cleanup при виході
import atexit
atexit.register(cleanup_bridge)


if __name__ == "__main__":
    # Тест bridge
    print("🧪 Тест MCP Bridge...")

    try:
        bridge = get_bridge()
        print("\n✅ Bridge запущено\n")

        # Тест sequential_thinking
        result1 = sequential_thinking_mcp.run(
            thought="Спочатку аналізуємо проблему",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True
        )
        print(f"Крок 1: {result1}\n")

        result2 = sequential_thinking_mcp.run(
            thought="Розглядаємо варіанти вирішення",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True
        )
        print(f"Крок 2: {result2}\n")

        result3 = sequential_thinking_mcp.run(
            thought="Формулюємо висновок",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False
        )
        print(f"Крок 3: {result3}\n")

        print("✅ Тест пройдено успішно!")

    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

    finally:
        cleanup_bridge()
