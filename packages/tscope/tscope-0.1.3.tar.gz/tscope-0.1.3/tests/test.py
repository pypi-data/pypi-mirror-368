import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tscope.main import TerminalScope

if __name__ == "__main__":
    scope = TerminalScope(
        ["sin(x)", "ramp", "0.5*sin(x + pi/3)"],
        ["$", "@", "?"],
        [-2, 2],
        refresh_mode=False,
        plot_width=70,
    )

    import math
    import time

    for _ in range(1000):
        x = time.time() * 4.0
        scope.plot([math.sin(x), 0.5 * math.sin(math.pi / 3 + x), x / 2 % 4 - 2])
        # s = scope.string([math.sin(x), 0.5 * math.sin(math.pi/3 + x), x / 2 % 4 - 2])
        # print(s, "add some endings")
        time.sleep(0.05)
