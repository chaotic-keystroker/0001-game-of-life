import numpy as np
from curses import wrapper
import scipy
from typing import Union


# MUSIC: 
# https://www.youtube.com/watch?v=x22zysfrVSk
# https://www.youtube.com/watch?v=GayJycHz04s


class GameOfLife:
    def __init__(self, board: Union[np.ndarray, str]):
        if isinstance(board, str):
            self.load(board)
        else:
            self.board = board.copy().astype(bool)
        self._kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    
    def step(self):
        cnt = scipy.signal.convolve2d(np.pad(self.board, 1, mode='wrap'), self._kernel, mode='valid')
        self.board = (cnt == 3) | (self.board & (cnt == 2))

    def toggle_cell(self, x, y):
        self.board[y, x] = not self.board[y, x]
    
    def clear(self):
        self.board.fill(False)
    
    def save(self, path):
        with open(str(path), 'wb') as f:
            np.save(f, self.board)
    
    def load(self, path):
        with open(str(path), 'rb') as f:
            self.board = np.load(f)

    def __str__(self):
        a = np.where(self.board, "█", " ")
        return "\n".join(["".join(row) for row in a])


def main(stdscr):
    # Clear screen
    # stdscr.clear()
    game = GameOfLife(np.random.randint(0, 2, (10, 10), dtype=bool))
    # game.draw(stdscr)
    # stdscr.refresh()
    # print(np.where(game.board, "#", " "))
    for i in range(30):
        print("-" * 50)
        game.step()
    #  game.step()


if __name__ == "__main__":
    main(None)
    #  wrapper(main)