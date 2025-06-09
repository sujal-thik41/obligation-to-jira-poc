import logging
from datetime import datetime
from typing import Optional

class ColorLogger:
    # ANSI escape codes for colors
    COLORS = {
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'RED': '\033[91m',
        'BLUE': '\033[94m',
        'PURPLE': '\033[95m',
        'CYAN': '\033[96m',
        'RESET': '\033[0m'
    }

    # Emojis for different log types
    EMOJIS = {
        'success': '✅',
        'info': 'ℹ️ ',
        'warning': '⚠️ ',
        'error': '❌',
        'processing': '⚙️ ',
        'chunk': '📄',
        'party': '👥',
        'obligation': '📝',
        'start': '🚀',
        'complete': '🏁',
        'retry': '🔄'
    }

    @staticmethod
    def log(msg: str, color: str = 'RESET', emoji: str = 'info', indent: int = 0) -> None:
        timestamp = datetime.now().strftime('%H:%M:%S')
        indent_str = '  ' * indent
        emoji_icon = ColorLogger.EMOJIS.get(emoji, '')
        color_code = ColorLogger.COLORS.get(color, ColorLogger.COLORS['RESET'])
        print(f"{color_code}{indent_str}{emoji_icon} [{timestamp}] {msg}{ColorLogger.COLORS['RESET']}")

    @staticmethod
    def success(msg: str, indent: int = 0) -> None:
        ColorLogger.log(msg, 'GREEN', 'success', indent)

    @staticmethod
    def info(msg: str, indent: int = 0) -> None:
        ColorLogger.log(msg, 'BLUE', 'info', indent)

    @staticmethod
    def warning(msg: str, indent: int = 0) -> None:
        ColorLogger.log(msg, 'YELLOW', 'warning', indent)

    @staticmethod
    def error(msg: str, indent: int = 0) -> None:
        ColorLogger.log(msg, 'RED', 'error', indent)

    @staticmethod
    def processing(msg: str, indent: int = 0) -> None:
        ColorLogger.log(msg, 'CYAN', 'processing', indent)

    @staticmethod
    def chunk(msg: str, indent: int = 0) -> None:
        ColorLogger.log(msg, 'PURPLE', 'chunk', indent)

    @staticmethod
    def party(msg: str, indent: int = 0) -> None:
        ColorLogger.log(msg, 'GREEN', 'party', indent)

    @staticmethod
    def obligation(msg: str, indent: int = 0) -> None:
        ColorLogger.log(msg, 'BLUE', 'obligation', indent)
