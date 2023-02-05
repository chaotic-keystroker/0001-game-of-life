from cellular_automata import GameOfLife
import pygame
import numpy as np
import sys
from enum import Enum

GRID_COLOR = (30, 30, 30)
COLORS = [(0, 0, 0), (255, 255, 255)]


class Controller:
    def __init__(self, game: GameOfLife, cellsize=10):
        self.game = game
        self.running = False
        (self.H, self.W) = game.board.shape
        self.S = cellsize
        self.canvas = pygame.display.set_mode((self.W * self.S, self.H * self.S))
        pygame.display.set_caption("John Conway's Game of Life")
        self.clock = pygame.time.Clock()

        self.current_state = np.ones_like(game.board, dtype=bool)
        self.canvas.fill(GRID_COLOR)
        self.draw(np.logical_not(self.current_state))  # empty board
        self.draw()

    def control(self, event: pygame.event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.running = not self.running
            if event.key == pygame.K_RIGHT:
                self.step()
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                pygame.quit()
                sys.exit(0)
            if event.key == pygame.K_c:
                self.game.clear()
                self.draw()
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            x = pos[0] // self.S
            y = pos[1] // self.S
            self.game.toggle_cell(x, y)
            self.draw()
    
    def draw(self, board = None):
        board = board if board is not None else self.game.board

        for y, x in zip(*np.where(board != self.current_state)):
            pygame.draw.rect(
                self.canvas, 
                COLORS[board[y, x]], 
                (x*self.S, y*self.S, self.S-1, self.S-1)
                )
        self.current_state = board.copy()
        pygame.display.update()

    def step(self):
        self.game.step()
        self.draw()
    
    def run(self):
        while True:
            for event in pygame.event.get():
                self.control(event)
            if self.running:
                self.step()
            self.clock.tick(30)



def main():
    pygame.init()
    W, H = (100, 50)
    # game = GameOfLife(np.zeros((H, W), dtype=bool))
    game = GameOfLife(np.zeros((H, W), dtype=bool))
    # game = GameOfLife(np.random.randint(0, 2, (H, W), dtype=bool))
    controler = Controller(game, 20)
    controler.run()


if __name__ == "__main__":
    main()