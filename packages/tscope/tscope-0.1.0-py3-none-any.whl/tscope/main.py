import os
from collections import deque


class TerminalScope():
    def __init__(self, variable_name: list, data_range: [int, int], data_symbol=None,
                 refresh_mode=False):
        # check input
        self.variable_count = len(variable_name)
        assert self.variable_count < 8, "only provide 7 colors!"
        self.data_range = data_range
        assert data_range[0] < data_range[1]
        if data_symbol is None:
            self.symbol_list = ['*'] * self.variable_count
        else:
            assert len(data_symbol) == self.variable_count, "Please check symbol length!"
            self.symbol_list = data_symbol

        self.refresh_mode = refresh_mode
        self.plot_length = os.get_terminal_size()[0] - 2 # plot region size
        self.plot_height = os.get_terminal_size()[1]
        self.lines = deque(maxlen=self.plot_height - 2)  # reserve one line for fixed info

        # print the top bar
        self.top_bar = ''.join([self._get_color_print(name, index).ljust(11 + int(self.plot_length/self.variable_count))
                                    for index, name in enumerate(variable_name)])
        print('\n', self.top_bar, '\n', '-'*(self.plot_length + 2), sep='')

    def _get_color_print(self, string, color_index:int):
        color_list = [31, 32, 33, 34, 35, 36, 37]
        return '\33[1;' + str(color_list[color_index]) + 'm' + string + '\033[0m'

    def plot(self, data):
        assert len(data) == self.variable_count, "Please check data length!"

        # get the position of each data
        pos_key = {}
        for index, d in enumerate(data):
            pos = round((d - self.data_range[0])/(self.data_range[1] - self.data_range[0]) * self.plot_length)
            pos_key[pos] = index

        # construct the line
        line = '|'
        for pos in range(self.plot_length):
            if pos in pos_key:
                index = pos_key[pos]
                line += self._get_color_print(self.symbol_list[index], index)
            else:
                line += ' '
        line += '|'

        # print the line
        if self.refresh_mode:
            self.lines.append(line)
            self._fresh_screen()
            print(self.top_bar)
            for line in self.lines:
                print(line)
        else:
            print(line)

    def _fresh_screen(self):
        if os.name == 'posix':  # deal with different platforms
            os.system('clear')
        else:
            os.system('cls')


if __name__ == "__main__":
    scope = TerminalScope(['sin(x)', '0.5*sin(x + pi/3)', 'ramp'],
                          [-2, 2],
                          ['$', '@', '?'],
                          refresh_mode=False)

    import math
    import time
    for _ in range(1000):
        x = time.time() * 4.0
        scope.plot([math.sin(x), 0.5 * math.sin(math.pi/3 + x), x / 2 % 4 - 2])
        time.sleep(0.05)
