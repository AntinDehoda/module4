"""
MCP Sequential Thinking Client

Справжній клієнт для підключення до MCP Sequential Thinking сервера.
"""

import asyncio
import os
from typing import Optional, List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPSequentialThinkingClient:
    """Клієнт для роботи з MCP Sequential Thinking сервером"""

    def __init__(self, server_script_path: Optional[str] = None):
        """
        Ініціалізація MCP клієнта

        Args:
            server_script_path: Шлях до скрипту MCP сервера
                               Якщо None, використовує npx для запуску офіційного сервера
        """
        self.server_script_path = server_script_path
        self.session: Optional[ClientSession] = None
        self._loop = None
        self._transport = None

    async def connect(self):
        """Підключення до MCP сервера"""
        if self.server_script_path:
            # Локальний Python сервер
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_script_path],
                env=None
            )
        else:
            # Офіційний сервер через npx
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-sequential-thinking"],
                env=None
            )

        # Підключення
        self._transport = await stdio_client(server_params)
        self.session = ClientSession(self._transport[0], self._transport[1])

        # Ініціалізація сесії
        await self.session.initialize()

        print("✅ Підключено до MCP Sequential Thinking сервера")

    async def disconnect(self):
        """Відключення від сервера"""
        if self.session:
            # Закриття транспорту
            if hasattr(self._transport[0], 'close'):
                await self._transport[0].close()
            if hasattr(self._transport[1], 'close'):
                await self._transport[1].close()
        print("🔌 Відключено від MCP сервера")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Отримати список доступних інструментів"""
        if not self.session:
            raise RuntimeError("Не підключено до сервера. Викличте connect() спочатку.")

        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Викликати інструмент MCP сервера

        Args:
            tool_name: Назва інструменту
            arguments: Аргументи для інструменту

        Returns:
            Результат виклику інструменту
        """
        if not self.session:
            raise RuntimeError("Не підключено до сервера. Викличте connect() спочатку.")

        result = await self.session.call_tool(tool_name, arguments)
        return result

    async def sequential_thinking(
        self,
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
        Виклик sequential_thinking інструменту

        Args:
            thought: Поточний крок мислення
            thought_number: Номер поточної думки
            total_thoughts: Очікувана кількість кроків
            next_thought_needed: Чи потрібний наступний крок
            is_revision: Чи переглядається попередня думка
            revises_thought: Номер думки для перегляду
            branch_from_thought: Номер думки для гілки
            branch_id: ID гілки
            needs_more_thoughts: Чи потрібні додаткові кроки

        Returns:
            Результат виклику
        """
        arguments = {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_thought_needed
        }

        # Додаткові параметри
        if is_revision:
            arguments["isRevision"] = is_revision
        if revises_thought is not None:
            arguments["revisesThought"] = revises_thought
        if branch_from_thought is not None:
            arguments["branchFromThought"] = branch_from_thought
        if branch_id is not None:
            arguments["branchId"] = branch_id
        if needs_more_thoughts:
            arguments["needsMoreThoughts"] = needs_more_thoughts

        result = await self.call_tool("sequential_thinking", arguments)

        # Повертаємо текстовий результат
        if hasattr(result, 'content') and result.content:
            return result.content[0].text if result.content else str(result)
        return str(result)


# Глобальний клієнт (singleton pattern)
_mcp_client: Optional[MCPSequentialThinkingClient] = None


def get_mcp_client() -> MCPSequentialThinkingClient:
    """Отримати глобальний екземпляр MCP клієнта"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPSequentialThinkingClient()
    return _mcp_client


async def test_mcp_client():
    """Тест MCP клієнта"""
    client = MCPSequentialThinkingClient()

    try:
        print("🔌 Підключення до MCP сервера...")
        await client.connect()

        print("\n📋 Доступні інструменти:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        print("\n🧠 Тест sequential thinking:")

        # Крок 1
        result1 = await client.sequential_thinking(
            thought="Аналізуємо вхідні дані та визначаємо основні елементи проблеми",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True
        )
        print(f"Крок 1: {result1}")

        # Крок 2
        result2 = await client.sequential_thinking(
            thought="Розглядаємо можливі підходи до вирішення проблеми",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True
        )
        print(f"Крок 2: {result2}")

        # Крок 3
        result3 = await client.sequential_thinking(
            thought="Формулюємо фінальний висновок та рекомендації",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False
        )
        print(f"Крок 3: {result3}")

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
