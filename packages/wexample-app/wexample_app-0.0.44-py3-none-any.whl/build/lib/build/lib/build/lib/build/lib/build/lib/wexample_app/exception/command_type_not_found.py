class CommandTypeNotFound(Exception):
    def __init__(self, command_name: str):
        self.command_name = command_name
        super().__init__(f"Unable to determine command type for: {command_name}")
