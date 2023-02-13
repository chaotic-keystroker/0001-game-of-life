import pygame
import numpy as np
import yaml
from cellular_automata import GameOfLife
from time import sleep
import sys


"""
Controls:
    SPACE - pause/resume
    RIGHT - step
    c - clear
    q - quit
    ESC - quit
    mouse - toggle cell, draw
"""

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Controller:
    def __init__(self, game: GameOfLife, conf: AttrDict):
        self.conf = conf
        self.game = game
        pygame.init()
        self.canvas = pygame.display.set_mode((conf.W * conf.CELL_SIZE, conf.H * conf.CELL_SIZE))
        pygame.display.set_caption("John Conway's Game of Life")
        self.clock = pygame.time.Clock()

        self.current_state = np.ones_like(game.board, dtype=bool)
        self.canvas.fill(self.conf.GRID_COLOR)
        self.draw(np.logical_not(self.current_state))  # empty board
        self.draw()  # draw the initial state
        self.running = False
        self.drawing = False
        self.mouse_cell = (-1, -1)
    
    def quit(self):
        pygame.quit()
        sys.exit(0)
    
    def draw(self, board=None):
        board = board if board is not None else self.game.board
        S, G = self.conf.CELL_SIZE, self.conf.GAP

        # draw only the cells that changed
        for y, x in zip(*np.where(board != self.current_state)):
            pygame.draw.rect(
                self.canvas, 
                self.conf.DEAD_LIVE_COLOR[board[y, x]],
                (x*S, y*S, S-G, S-G),
                )
        self.current_state = board.copy()
        pygame.display.update()

    def get_cell(self):
        pos = pygame.mouse.get_pos()
        x = pos[0] // self.conf.CELL_SIZE
        y = pos[1] // self.conf.CELL_SIZE
        return x, y
    
    def control(self, event):
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.quit()
            elif event.key == pygame.K_SPACE:
                self.running = not self.running
            elif event.key == pygame.K_RIGHT:
                self.step()
            elif event.key == pygame.K_c:
                self.game.clear()
                self.draw()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.drawing = True
                x, y = self.get_cell()
                self.game.toggle_cell(x, y)
                self.draw()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.drawing = False
                self.draw()
        elif event.type == pygame.MOUSEMOTION:
            if self.drawing:
                cell = self.get_cell()
                if cell != self.mouse_cell:
                    self.mouse_cell = cell
                    self.game.toggle_cell(*cell)
                    self.draw()
    
    def step(self):
        self.game.step()
        self.draw()
    
    def run(self):
        while True:
            for event in pygame.event.get():
                self.control(event)
            if self.running:
                self.step()
            self.clock.tick(self.conf.FPS)

def main():
    with open("src/config.yaml", "r") as f:
        config = AttrDict(yaml.safe_load(f))
    board = np.random.randint(0, 2, size=(config.H, config.W))
    game = GameOfLife(board)
    controller = Controller(game, config)
    controller.run()


if __name__ == "__main__":
    main()