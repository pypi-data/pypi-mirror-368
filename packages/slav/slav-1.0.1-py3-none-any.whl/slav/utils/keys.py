class Key:
    ENTER = '\r'
    ESCAPE = '\033'
    BACKSPACE = '\x7f'
    DELETE = '\033[3~'
    TAB = '\t'
    SPACE = ' '
    
    UP = '\033[A'
    DOWN = '\033[B'
    RIGHT = '\033[C'
    LEFT = '\033[D'
    
    HOME = '\033[H'
    END = '\033[F'
    PAGE_UP = '\033[5~'
    PAGE_DOWN = '\033[6~'
    
    F1 = '\033OP'
    F2 = '\033OQ'
    F3 = '\033OR'
    F4 = '\033OS'
    F5 = '\033[15~'
    F6 = '\033[17~'
    F7 = '\033[18~'
    F8 = '\033[19~'
    F9 = '\033[20~'
    F10 = '\033[21~'
    F11 = '\033[23~'
    F12 = '\033[24~'
    
    @staticmethod
    def is_printable(key: str) -> bool:
        if len(key) != 1:
            return False
        return 32 <= ord(key) <= 126
        
    @staticmethod
    def is_navigation(key: str) -> bool:
        return key in [Key.UP, Key.DOWN, Key.LEFT, Key.RIGHT, Key.HOME, Key.END, Key.PAGE_UP, Key.PAGE_DOWN]
        
    @staticmethod
    def is_function(key: str) -> bool:
        return key in [Key.F1, Key.F2, Key.F3, Key.F4, Key.F5, Key.F6, Key.F7, Key.F8, Key.F9, Key.F10, Key.F11, Key.F12]
