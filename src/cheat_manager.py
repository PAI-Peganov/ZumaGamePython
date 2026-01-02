class CheatManager:
    def __init__(self):
        self.infinite_time = False
        self.party = False
        self.seq = [
            "UP", "UP", "DOWN", "DOWN", "LEFT", "RIGHT", "LEFT", "RIGHT",
            "B", "A"
        ]
        self.i = 0

    def feed_sequences(self, key_name: str) -> bool:
        if key_name == self.seq[self.i]:
            self.i += 1
            if self.i == len(self.seq):
                self.i = 0
                self.party = not self.party
                return True
        else:
            self.i = 0
        return False
