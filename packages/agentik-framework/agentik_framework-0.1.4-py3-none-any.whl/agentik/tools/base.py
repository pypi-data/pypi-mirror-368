# agentik/tools/base.py
class Tool:
    name: str = "base"
    description: str = "Base tool"

    def run(self, input_text: str) -> str:
        raise NotImplementedError
