class Branch(list):
    def __init__(self):
        super().__init__()
        self.remaining_eventualities = set()
        self.eventualities = set()  # Puede que no se haga asi
        self.literals = set()

    def append(self, tl_Set):
        self.append(tl_Set)

    def pop(self):
        return self.pop()

    def has_fulfill_all_eventualities(self):
        return len(self.remaining_eventualities) == 0
