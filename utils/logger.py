import shutil, sys

COLORS = {
    'white': '\033[00m',
    'green': '\033[92m',
    'red': '\033[91m',
    'yellow': '\033[93m'
}

RESET = "\033[0m"

def log_over(text, color='white'):
    sys.stdout.write(f'{COLORS[color]}{text}{RESET}')

def log(text, color='white'):
    print(f'{COLORS[color]}{text}{RESET}')

def clean():
    sys.stdout.write(f'\r{" " * shutil.get_terminal_size()[0]}')