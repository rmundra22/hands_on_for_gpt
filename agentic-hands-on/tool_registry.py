from 
class ToolRegistry:
    def __init__(self, tools: list[BaseTool]):
        self._tools = {tool.name: tool for tool in tools}

    def schemas(self) -> list[dict]:
        return [tool.schema() for tool in self._tools.values()]

    def execute(self, name: str, args: dict) -> dict:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not registered")
        return self._tools[name].run(**args)
