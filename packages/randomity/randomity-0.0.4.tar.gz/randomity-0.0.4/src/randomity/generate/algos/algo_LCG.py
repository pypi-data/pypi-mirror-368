class _LCG:
    def __init__(self, seed: int):
        self.a = 1103515245
        self.c = 12345
        self.m = 2**31
        
        self.x = seed

    def next_int(self) -> int:
        self.x = (self.a * self.x + self.c) % self.m
        return self.x