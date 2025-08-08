from __future__ import annotations
from .core import Pattern
import random

class LSystem:
    def __init__(self, rule: str = "N[-N++N]-N", seed="N"):
        self.rule = rule
        self.seed = seed
        self.string = seed

        self.reset()

    def __repr__(self):
        return ("LSystem(%s, %s)" % (repr(self.rule), repr(self.seed)))

    def reset(self):
        self.pos = 0
        self.stack = []
        self.state = 0

    def iterate(self, count: int = 3):
        if self.rule.count("[") != self.rule.count("]"):
            raise ValueError("Imbalanced brackets in rule string: %s" % self.rule)

        for n in range(count):
            string_new = ""
            for char in self.string:
                string_new = string_new + self.rule if char == "N" else string_new + char

            self.string = string_new

    def __next__(self):
        while self.pos < len(self.string):
            token = self.string[self.pos]
            self.pos = self.pos + 1

            if token == 'N':
                return self.state
            elif token == '_':
                return None
            elif token == '-':
                self.state -= 1
            elif token == '+':
                self.state += 1
            elif token == '?':
                self.state += random.choice([-1, 1])
            elif token == '[':
                self.stack.append(self.state)
            elif token == ']':
                self.state = self.stack.pop()

        raise StopIteration

class PLSystem(Pattern):
    """ PLSystem: Formal grammars based on Lindenmayer systems, modelling plant growth."""

    def __init__(self, rule: str, depth: int = 3, loop: bool = True):
        self.rule = rule
        self.depth = depth
        self.loop = loop
        self.lsys = None
        self.reset()

    def __repr__(self):
        return ("PLSystem(%s, %s, %s)" % (repr(self.rule), self.depth, self.loop))

    def reset(self):
        self.lsys = LSystem(self.rule, "N")
        self.lsys.iterate(self.depth)

    def __next__(self):
        n = next(self.lsys)
        if self.loop and n is None:
            self.lsys.reset()
            n = next(self.lsys)

        return None if n is None else n
