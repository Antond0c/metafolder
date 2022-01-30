from .methods import safe_get_from_array


class InData:
    """contains data from input line,\n
    reads prompt input and creates different information on it."""

    def __init__(self):
        self.line = input().strip()
        self.args = self.line.split(" ")
        self.size = len(self.args)
        self.has_multi = self.size > 1
        self.first = self.command = self.second = safe_get_from_array(self.args, 0)
        self.second = safe_get_from_array(self.args, 1)
        self.third = safe_get_from_array(self.args, 2)
        self.params = None
        self.is_blank = not self.line

    def init_params(self):
        """?"""
        if not self.params and self.size > 1:
            self.params = self.args[1:]
