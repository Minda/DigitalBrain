#!/usr/bin/env python3
"""
Smart terminal title setter that detects and supports multiple terminal types
"""
import os
import sys
import subprocess


def detect_terminal_type():
    """Detect which terminal environment we're running in"""

    # Check for VS Code
    if os.getenv('TERM_PROGRAM') == 'vscode' or os.getenv('VSCODE_INJECTION'):
        return 'vscode'

    # Check for tmux
    if os.getenv('TMUX'):
        return 'tmux'

    # Check for screen
    if os.getenv('STY'):
        return 'screen'

    # Check for iTerm2
    if os.getenv('TERM_PROGRAM') == 'iTerm.app':
        return 'iterm2'

    # Check for Terminal.app
    if os.getenv('TERM_PROGRAM') == 'Apple_Terminal':
        return 'terminal_app'

    # Default to standard ANSI escape codes
    return 'standard'


def set_terminal_title(title):
    """Set terminal title based on detected terminal type"""

    terminal_type = detect_terminal_type()

    if terminal_type == 'vscode':
        # VS Code doesn't support terminal title changes via escape codes
        return {
            'success': False,
            'terminal': 'VS Code',
            'message': 'VS Code integrated terminal does not support title changes'
        }

    elif terminal_type == 'tmux':
        # tmux uses rename-window command
        try:
            result = subprocess.run(
                ['tmux', 'rename-window', title],
                capture_output=True,
                text=True,
                check=False
            )
            return {
                'success': result.returncode == 0,
                'terminal': 'tmux',
                'message': f'tmux window renamed to: {title}' if result.returncode == 0 else f'Failed to rename tmux window: {result.stderr}'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'terminal': 'tmux',
                'message': 'tmux command not found'
            }

    elif terminal_type == 'screen':
        # GNU screen uses screen -X title command
        try:
            result = subprocess.run(
                ['screen', '-X', 'title', title],
                capture_output=True,
                text=True,
                check=False
            )
            return {
                'success': result.returncode == 0,
                'terminal': 'screen',
                'message': f'screen window renamed to: {title}' if result.returncode == 0 else f'Failed to rename screen window: {result.stderr}'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'terminal': 'screen',
                'message': 'screen command not found'
            }

    else:
        # Standard terminals (iTerm2, Terminal.app, most Linux terminals)
        # Use ANSI escape codes
        try:
            if sys.platform == "darwin":
                # macOS - use both escape sequences for compatibility
                os.system(f'echo -ne "\\033]0;{title}\\007"')
                os.system(f'printf "\\e]1;{title}\\a"')
                terminal_name = 'iTerm2' if terminal_type == 'iterm2' else 'Terminal.app' if terminal_type == 'terminal_app' else 'macOS Terminal'
            elif sys.platform.startswith("linux"):
                # Linux
                os.system(f'echo -ne "\\033]0;{title}\\007"')
                terminal_name = 'Linux Terminal'
            else:
                return {
                    'success': False,
                    'terminal': 'unknown',
                    'message': f'Platform {sys.platform} not supported'
                }

            return {
                'success': True,
                'terminal': terminal_name,
                'message': f'Terminal title set to: {title}'
            }
        except Exception as e:
            return {
                'success': False,
                'terminal': terminal_type,
                'message': f'Error setting title: {str(e)}'
            }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: set_terminal_title.py \"Title\"")
        print("\nDetected terminal type:", detect_terminal_type())
        sys.exit(1)

    title = sys.argv[1]
    result = set_terminal_title(title)

    print(f"Terminal: {result['terminal']}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")

    sys.exit(0 if result['success'] else 1)
