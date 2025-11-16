"""
Color system for CLI with cross-platform support.

Attempts to use colorama for Windows compatibility, falls back to ANSI codes,
and finally falls back to no colors if neither works.

Author: Rafael Correa
Date: November 16, 2025
"""

import sys

# ──────────────────────────────────────────────────────
# Attempt to import colorama (cross-platform solution)
# ──────────────────────────────────────────────────────
try:
    from colorama import Fore, Style, init as colorama_init
    # Initialize colorama for Windows support
    colorama_init(autoreset=True)
    USE_COLORAMA = True
    USE_COLORS = True
except ImportError:
    USE_COLORAMA = False
    # Check if terminal supports ANSI codes (Mac/Linux/Windows Terminal)
    USE_COLORS = sys.stdout.isatty()


class Colors:
    """
    Utilities for coloring terminal text with cross-platform support.
    
    Priority:
    1. colorama (if installed) - works on all platforms
    2. ANSI codes (if terminal supports it) - Mac/Linux/modern Windows
    3. No colors (fallback) - old Windows cmd.exe
    
    Usage:
        print(Colors.red("Error"))
        print(Colors.green("Success"))
        print(Colors.bold(Colors.blue("Title")))
    
    Installation for Windows:
        pip install colorama
    """
    
    # ──────────────────────────────────────────────────────
    # Color Codes (colorama or ANSI)
    # ──────────────────────────────────────────────────────
    if USE_COLORAMA:
        # Use colorama (cross-platform)
        RED = Fore.RED
        GREEN = Fore.GREEN
        YELLOW = Fore.YELLOW
        BLUE = Fore.BLUE
        MAGENTA = Fore.MAGENTA
        CYAN = Fore.CYAN
        WHITE = Fore.WHITE
        GRAY = Fore.LIGHTBLACK_EX
        
        BOLD = Style.BRIGHT
        UNDERLINE = ''  # colorama doesn't support underline
        RESET = Style.RESET_ALL
    elif USE_COLORS:
        # Use ANSI codes (Mac/Linux/Windows Terminal)
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        GRAY = '\033[90m'
        
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        RESET = '\033[0m'
    else:
        # No colors (fallback for old Windows cmd.exe)
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        GRAY = ''
        
        BOLD = ''
        UNDERLINE = ''
        RESET = ''
    
    # ──────────────────────────────────────────────────────
    # Helper Methods - Basic Colors
    # ──────────────────────────────────────────────────────
    
    @classmethod
    def red(cls, text: str) -> str:
        """Returns text in red."""
        return f"{cls.RED}{text}{cls.RESET}"
    
    @classmethod
    def green(cls, text: str) -> str:
        """Returns text in green."""
        return f"{cls.GREEN}{text}{cls.RESET}"
    
    @classmethod
    def yellow(cls, text: str) -> str:
        """Returns text in yellow."""
        return f"{cls.YELLOW}{text}{cls.RESET}"
    
    @classmethod
    def blue(cls, text: str) -> str:
        """Returns text in blue."""
        return f"{cls.BLUE}{text}{cls.RESET}"
    
    @classmethod
    def magenta(cls, text: str) -> str:
        """Returns text in magenta."""
        return f"{cls.MAGENTA}{text}{cls.RESET}"
    
    @classmethod
    def cyan(cls, text: str) -> str:
        """Returns text in cyan."""
        return f"{cls.CYAN}{text}{cls.RESET}"
    
    @classmethod
    def gray(cls, text: str) -> str:
        """Returns text in gray."""
        return f"{cls.GRAY}{text}{cls.RESET}"
    
    @classmethod
    def white(cls, text: str) -> str:
        """Returns text in white."""
        return f"{cls.WHITE}{text}{cls.RESET}"
    
    # ──────────────────────────────────────────────────────
    # Helper Methods - Styles
    # ──────────────────────────────────────────────────────
    
    @classmethod
    def bold(cls, text: str) -> str:
        """Returns text in bold."""
        return f"{cls.BOLD}{text}{cls.RESET}"
    
    @classmethod
    def underline(cls, text: str) -> str:
        """Returns text underlined (not supported with colorama)."""
        if USE_COLORAMA:
            # colorama doesn't support underline, return as-is
            return text
        return f"{cls.UNDERLINE}{text}{cls.RESET}"
    
    # ──────────────────────────────────────────────────────
    # Helper Methods - Semantic Combinations
    # ──────────────────────────────────────────────────────
    
    @classmethod
    def success(cls, text: str) -> str:
        """Returns text formatted for success (green + bold)."""
        return f"{cls.BOLD}{cls.GREEN}{text}{cls.RESET}"
    
    @classmethod
    def error(cls, text: str) -> str:
        """Returns text formatted for error (red + bold)."""
        return f"{cls.BOLD}{cls.RED}{text}{cls.RESET}"
    
    @classmethod
    def warning(cls, text: str) -> str:
        """Returns text formatted for warning (yellow)."""
        return f"{cls.YELLOW}{text}{cls.RESET}"
    
    @classmethod
    def info(cls, text: str) -> str:
        """Returns text formatted for information (cyan)."""
        return f"{cls.CYAN}{text}{cls.RESET}"
    
    @classmethod
    def header(cls, text: str) -> str:
        """Returns text formatted for header (blue + bold)."""
        return f"{cls.BOLD}{cls.BLUE}{text}{cls.RESET}"
    
    # ──────────────────────────────────────────────────────
    # Utility Methods
    # ──────────────────────────────────────────────────────
    
    @classmethod
    def is_color_supported(cls) -> bool:
        """Returns True if colors are supported in the current terminal."""
        return USE_COLORS
    
    @classmethod
    def get_backend(cls) -> str:
        """Returns the color backend being used: 'colorama', 'ansi', or 'none'."""
        if USE_COLORAMA:
            return 'colorama'
        elif USE_COLORS:
            return 'ansi'
        else:
            return 'none'
