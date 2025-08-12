def strip_ansi_sequences(text: str) -> str:
    """Remove ANSI escape sequences from the text."""

    import re
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


def ansi_centered_line(line: str, terminal_width: int) -> str:
    """Center text in terminal, accounting for invisible ANSI sequences."""

    visible_length = len(strip_ansi_sequences(line))
    total_padding = max(0, (terminal_width - visible_length) // 2)
    return ' ' * total_padding + line
