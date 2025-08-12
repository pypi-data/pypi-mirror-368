class WithIndent:
    log_indent: int = 0
    _indent_string: str = "  "

    def log_indent_up(self, number: int = 1) -> None:
        self.log_indent += number

    def log_indent_down(self, number: int = 1) -> None:
        self.log_indent -= number

    def build_indent(self, increment: int = 0) -> str:
        return str(self._indent_string * (self.log_indent + increment))
