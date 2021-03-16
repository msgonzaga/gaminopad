
class StateRegister:
    def __init__(self, memory_len=20):
        self.states = []
        self.max_len = memory_len
        self.pointer = -1

    def reset(self):
        self.states = []
        self.pointer = -1

    def push_state(self, values):
        if not self.states or values != self.states[self.pointer]:
            self.states = self.states[0:self.pointer + 1]
            self.states.append(values)
            self.pointer += 1
            if len(self.states) > self.max_len:
                self.states = self.states[1:]
                self.pointer -= 1

    def undo(self):
        if self.pointer - 1 >= 0:
            self.pointer -= 1
            return self.states[self.pointer]

    def redo(self):
        if self.pointer + 1 < len(self.states):
            self.pointer += 1
            return self.states[self.pointer]