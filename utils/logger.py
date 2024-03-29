from settings import LOGGING

COLORS = {
    'white': '\033[00m',
    'green': '\033[92m',
    'red': '\033[91m',
    'yellow': '\033[93m'
}

RESET = '\033[0m'
CLEAR = '\x1b[2K'

def log_over(text, color='white'):
    if LOGGING:
        print(f'{COLORS[color]}{text}{RESET}', end='')

def log(text, color='white'):
    if LOGGING:
        print(f'{COLORS[color]}{text}{RESET}')