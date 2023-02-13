import pygame
import pygame.midi
import numpy as np
import yaml
from cellular_automata import GameOfLife
from time import sleep
import sys
import datetime


"""
Controls:
    SPACE - pause/resume
    RIGHT - step
    c - clear
    r - load last saved state (before SPACE)
    q - quit
    CTRL + S - save the current state as as file
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
        pygame.midi.init()
        port = pygame.midi.get_default_output_id()
        self.midi_out = pygame.midi.Output(port, 0)

        self.grid_size = conf.W * conf.CELL_SIZE, conf.H * conf.CELL_SIZE

        if conf.FULLSCREEN:
            self.canvas = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            displayInfo = pygame.display.Info()
            W, H = displayInfo.current_w, displayInfo.current_h
            self.grid_offset = (W - conf.W * conf.CELL_SIZE) // 2, (H - conf.H * conf.CELL_SIZE) // 2
        else:
            self.grid_offset = conf.CELL_SIZE, conf.CELL_SIZE
            W, H = self.grid_size[0] + 2*self.grid_offset[0], self.grid_size[1] + 2*self.grid_offset[1]
            self.canvas = pygame.display.set_mode((W, H))
        pygame.display.set_caption("John Conway's Game of Life")

        self.clock = pygame.time.Clock()

        self.saved_state = game.board.copy()
        self.current_state = np.ones_like(game.board, dtype=bool)
        self.draw_background()
        self.clock.tick(self.conf.FPS)
        self.draw(np.logical_not(self.current_state))  # empty board
        self.draw()  # draw the initial state
        self.running = False
        self.drawing = False
        self.mouse_cell = (-1, -1)

    def draw_background(self):
        (x, y), (w, h) = self.grid_offset, self.grid_size

        self.canvas.fill([0, 0, 0])
        pygame.display.update()
        pygame.draw.rect(
            self.canvas, 
            self.conf.GRID_COLOR,
            (x, y, w, h),
        )
        
        S = self.conf.GAP * 2
        pygame.draw.lines(
            self.canvas, 
            (255, 255, 255), 
            True,
            ((x-S, y-S), (x-S, y+h),(x+w, y+h),(x+w, y-S)),
            S,
        )
        pygame.display.update()
    
    def quit(self):
        self.silence()
        self.midi_out.abort()
        self.midi_out.close()
        pygame.midi.quit()
        pygame.quit()
        sys.exit(0)
    
    def draw(self, board=None):
        board = board if board is not None else self.game.board
        ox, oy = self.grid_offset
        S, G = self.conf.CELL_SIZE, self.conf.GAP
        msg = [self.midi_out.note_off, self.midi_out.note_on]

        # draw only the cells that changed
        for y, x in zip(*np.where(board != self.current_state)):
            msg[board[y, x]](note=x%128, velocity=(127-y)%128, channel=0)
            pygame.draw.rect(
                self.canvas, 
                self.conf.DEAD_LIVE_COLOR[int(board[y, x])],
                (ox+x*S, oy+y*S, S-G, S-G),
                )
        self.current_state = board.copy()
        pygame.display.update()

    def get_cell(self):
        x, y = pygame.mouse.get_pos()
        x = (x - self.grid_offset[0]) // self.conf.CELL_SIZE
        y = (y - self.grid_offset[1]) // self.conf.CELL_SIZE
        return x, y
    
    def silence(self):
        for i in range(128):
            self.midi_out.note_off(note=i, velocity=127, channel=0)
    
    def control(self, event):
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.quit()
            elif event.key == pygame.K_SPACE:
                if not self.running:
                    self.saved_state = self.game.board.copy()
                self.running = not self.running
            elif event.key == pygame.K_RIGHT:
                self.step()
            elif event.key == pygame.K_c:
                self.silence()
                self.game.clear()
                self.draw()
            elif event.key == pygame.K_r:
                self.game.board = self.saved_state.copy()
                self.draw()
            elif event.key == pygame.K_s:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    filename = f"game_of_life_{datetime.datetime.now().isoformat()}.npy"
                    self.game.save(filename)
                    print(f'saved as: "{filename}"')
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.drawing = True
                self.draw()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.drawing = False
                cell = self.get_cell()
                if cell != self.mouse_cell:
                    self.game.toggle_cell(*cell)
                    self.draw()
                self.mouse_cell = (-1, -1)
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
    board = np.zeros((config.H, config.W), dtype=bool)
    game = GameOfLife(board)
    game = GameOfLife.from_file("thank_you.npy")
    controller = Controller(game, config)
    controller.run()


if __name__ == "__main__":
    main()