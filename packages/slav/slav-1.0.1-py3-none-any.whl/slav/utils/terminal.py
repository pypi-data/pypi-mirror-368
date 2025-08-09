import sys
import os
import signal
from typing import Tuple, Optional

try:
    import termios
    import tty
    import select
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False


class Terminal:
    def __init__(self):
        self._original_settings = None
        self._size_cache = None
        
    def __enter__(self):
        self.setup()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        
    def setup(self):
        if sys.platform != 'win32' and HAS_TERMIOS:
            self._original_settings = termios.tcgetattr(sys.stdin.fileno())
            tty.setraw(sys.stdin.fileno())
        
        sys.stdout.write('\033[?1049h')
        sys.stdout.write('\033[2J')
        sys.stdout.write('\033[H')
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
        
        if hasattr(signal, 'SIGWINCH'):
            signal.signal(signal.SIGWINCH, self._handle_resize)
        
    def cleanup(self):
        sys.stdout.write('\033[?25h')
        sys.stdout.write('\033[?1049l')
        sys.stdout.flush()
        
        if sys.platform != 'win32' and HAS_TERMIOS and self._original_settings:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._original_settings)
            
    def _handle_resize(self, signum, frame):
        self._size_cache = None
        
    def get_size(self) -> Tuple[int, int]:
        if self._size_cache is None:
            try:
                size = os.get_terminal_size()
                self._size_cache = (size.columns, size.lines)
            except OSError:
                self._size_cache = (80, 24)
        return self._size_cache
        
    def clear(self):
        sys.stdout.write('\033[2J')
        sys.stdout.write('\033[H')
        sys.stdout.flush()
        
    def move_cursor(self, x: int, y: int):
        sys.stdout.write(f'\033[{y + 1};{x + 1}H')
        
    def hide_cursor(self):
        sys.stdout.write('\033[?25l')
        
    def show_cursor(self):
        sys.stdout.write('\033[?25h')
        
    def get_key(self) -> Optional[str]:
        if sys.platform == 'win32':
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x00' or key == b'\xe0':
                    key = msvcrt.getch()
                    return f'special_{ord(key)}'
                return key.decode('utf-8', errors='ignore')
            return None
        else:
            if HAS_TERMIOS and select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                if key == '\033':
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key += sys.stdin.read(1)
                        if key == '\033[':
                            key += sys.stdin.read(1)
                return key
            return None
            
    def flush(self):
        sys.stdout.flush()
