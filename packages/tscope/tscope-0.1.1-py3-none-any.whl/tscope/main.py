import os
from collections import deque


class TerminalScope():
    """A simple Python-based oscilloscope for visualizing dynamic data in the terminal.
    https://github.com/sszxc/TerminalScope
    """
    def __init__(self, variable_name: list, data_symbol=None, data_range: tuple[float, float]=[-1, 1],
                 auto_range=True, plot_width=None, refresh_mode=False, no_top_bar=False, no_color=False):
        # check input
        self.variable_count = len(variable_name)
        self.no_color = no_color
        if not no_color:
            assert self.variable_count < 8, "only provide 7 colors!"
        # data range
        self.data_range = data_range
        assert data_range[0] < data_range[1]
        self.auto_range = auto_range
        # symbol
        if data_symbol is None:
            self.symbol_list = ['*'] * self.variable_count
        else:
            assert len(data_symbol) == self.variable_count, "Please check symbol length!"
            self.symbol_list = data_symbol
        # print config
        self.refresh_mode = refresh_mode
        if plot_width is not None:
            self.plot_width = plot_width
        else:
            self.plot_width = os.get_terminal_size()[0] - 2 # plot region size
        self.plot_height = os.get_terminal_size()[1]  # only for refresh mode
        self.lines = deque(maxlen=self.plot_height - 2)  # reserve one line for fixed info
        # construct top bar
        if not no_top_bar:
            column_width = int(self.plot_width/self.variable_count)
            self.top_bar = ''.join([self._get_color_print(name, index) + ' '*(column_width - len(name))
                                        for index, name in enumerate(variable_name)])
            print('\n', self.top_bar, '\n', '-'*(self.plot_width + 2), sep='')

    def _get_color_print(self, string, color_index:int):
        if self.no_color:
            return string
        color_list = [31, 32, 33, 34, 35, 36, 37]
        return '\33[1;' + str(color_list[color_index]) + 'm' + string + '\033[0m'

    def plot(self, data):
        # construct the line
        line = self.string(data)
        # print the line
        if self.refresh_mode:
            self.lines.append(line)
            self._fresh_screen()
            if hasattr(self, 'top_bar'):
                print(self.top_bar)
            for line in self.lines:
                print(line)
        else:
            print(line)

    def string(self, data):
        assert len(data) == self.variable_count, "Please check data length!"
        if self.auto_range:
            self.data_range = [min(*data, self.data_range[0]), max(*data, self.data_range[1])]
        # get the position of each data
        pos_key = {}
        for index, d in enumerate(data):
            pos = round((d - self.data_range[0])/(self.data_range[1] - self.data_range[0]) * self.plot_width)
            pos_key[pos] = index
        # construct the line
        line = '|'
        for pos in range(self.plot_width):
            if pos in pos_key:
                index = pos_key[pos]
                line += self._get_color_print(self.symbol_list[index], index)
            else:
                line += ' '
        line += '|'
        return line

    def _fresh_screen(self):
        if os.name == 'posix':  # deal with different platforms
            os.system('clear')
        else:
            os.system('cls')


if __name__ == "__main__":
    scope = TerminalScope(['sin(x)', 'ramp', '0.5*sin(x + pi/3)'],
                          ['$', '@', '?'],
                          [-2, 2],
                          refresh_mode=False, plot_width=70)

    import math
    import time
    for _ in range(1000):
        x = time.time() * 4.0
        scope.plot([math.sin(x), 0.5 * math.sin(math.pi/3 + x), x / 2 % 4 - 2])
        # s = scope.string([math.sin(x), 0.5 * math.sin(math.pi/3 + x), x / 2 % 4 - 2])
        # print(s, "add some endings")
        time.sleep(0.05)
