import numpy as np
import scipy


class GameOfLife:
    def __init__(self, board):
        # 0 = dead, 1 = alive
        self.board = board.copy().astype(bool)
        # convolution kernel - counts the number of alive neighbors
        self._kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    
    def step(self):
        # wrap maked the board toroidal - the edges are connected
        board = np.pad(self.board, 1, mode='wrap')
        cnt = scipy.signal.convolve2d(board, self._kernel, mode='valid')
        # Any live cell with two or three live neighbours survives.
        # Any dead cell with three live neighbours becomes a live cell.
        # these rules cam be simplified
        self.board = (cnt == 3) | ((cnt == 2) & (self.board))
    
    def clear(self):
        self.board.fill(False)
    
    def toggle_cell(self, x, y):
        self.board[y, x] = not self.board[y, x]
    
    def __str__(self):
        arr = np.where(self.board, '#', ' ')
        return "\n".join(["".join(row) for row in arr])


def main():
    game = GameOfLife(np.random.randint(0, 2, size=(10, 10)))
    for i in range(30):
        print("-" * 50)
        game.step()
        print(game)


if __name__ == "__main__":
    main()