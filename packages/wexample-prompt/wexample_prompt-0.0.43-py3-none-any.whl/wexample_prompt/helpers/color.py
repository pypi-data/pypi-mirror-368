from typing import List


def color_apply_to_lines(text: str, colors: List[str]) -> str:
    """Apply multiple colors to the lines of the text."""
    from colorama import Style

    lines = text.split('\n')
    gradient_lines = []

    for i, line in enumerate(lines):
        color = colors[i % len(colors)]  # Cycle through colors
        gradient_lines.append(f"{color}{line}{Style.RESET_ALL}")

    return '\n'.join(gradient_lines)
