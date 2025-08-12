class CommandResolverNotFound(Exception):
    def __init__(self, command_type: str):
        self.command_type = command_type
        super().__init__(f"No resolver found for command type: {command_type}")
