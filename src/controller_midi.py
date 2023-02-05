from automata import GameOfLife
import pygame
import pygame.midi
import numpy as np
import sys
import datetime


GRID_COLOR = (30, 30, 30)
COLORS = [(0, 0, 0), (255, 255, 255)]


"""
Controls:
    SPACE: start/stop
    s: save board
    r: reset - load saved board
    CTRL+s: save board as file (filename: game_of_life_<datetime>.npy)
    RIGHT ARROW: step
    c: clear board
    q: quit
    ESC: quit
    mouse: draw (toggle, drag)


if you want to load the game from the file, instead of "run_game_of_life()" in the __main__ section,
use: load_game_of_life("filepath"), where filepath is the path to the file with the saved board.
"""

class ControllerMidi:
    def __init__(self, game: GameOfLife, cellsize=10):
        self.game = game
        self.running = False
        self.drawing = False
        self.mouse_cell = (0, 0)
        self.saved_board = self.game.board.copy()
        self.H, self.W = game.board.shape
        self.S = cellsize
        self.current_state = np.ones_like(game.board, dtype=bool)

        pygame.init()
        pygame.midi.init()
        pygame.display.set_caption("John Conway's Game of Life")
        port = pygame.midi.get_default_output_id()
        self.midi_out = pygame.midi.Output(port, 0)
        self.canvas = pygame.display.set_mode((self.W * self.S, self.H * self.S))
        self.clock = pygame.time.Clock()
        # -----
        self.canvas.fill(GRID_COLOR)
        self.draw_play(np.logical_not(self.current_state))   # empty board, all notes off
        self.draw_play()


    def quit(self):
        for n in range(127):
            self.midi_out.note_off(note=n, velocity=127, channel=0)
        self.midi_out.abort()
        self.midi_out.close()
        pygame.midi.quit()
        pygame.quit()
        sys.exit(0)
    
    def get_cell(self):
        x, y = pygame.mouse.get_pos()
        return x // self.S, y // self.S

    def control(self, event: pygame.event):
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not self.running:
                    self.board_before_run = self.game.board.copy()
                self.running = not self.running
            elif event.key == pygame.K_RIGHT:
                self.step()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.quit()
            elif event.key == pygame.K_r:
                if self.running:
                    self.running = False
                self.game.board = self.saved_board.copy()
                self.draw_play()
            elif event.key == pygame.K_c:
                self.game.clear()
                self.draw_play()
            elif event.key == pygame.K_s:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    filename = f"game_of_life_{datetime.datetime.now().isoformat()}.npy"
                    self.game.save(filename)
                    print(f'saved as: "{filename}"')
                else:
                    self.saved_board = self.game.board.copy()
                    print("board saved")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.drawing = True
                self.mouse_cell = self.get_cell()
                self.game.toggle_cell(*self.mouse_cell)
                self.draw_play() 
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.drawing = False
                self.draw_play() 
        elif event.type == pygame.MOUSEMOTION:
            if self.drawing:
                cell = self.get_cell()
                if cell != self.mouse_cell:
                    self.mouse_cell = cell
                    self.game.toggle_cell(*cell)
                    self.draw_play()
    
    def draw_play(self, board = None):
        board = board if board is not None else self.game.board
        f = [self.midi_out.note_off, self.midi_out.note_on]

        for y, x in zip(*np.where(board != self.current_state)):
            f[board[y, x]](note=x%128, velocity=(127-y)%128, channel=0)
            pygame.draw.rect(
                self.canvas, 
                COLORS[board[y, x]], 
                (x*self.S, y*self.S, self.S-1, self.S-1)
                )
        self.current_state = board.copy()
        pygame.display.update()

    def step(self):
        self.game.step()
        self.draw_play()
    
    def run(self):
        while True:
            for event in pygame.event.get():
                self.control(event)
            if self.running:
                self.step()
            self.clock.tick(30)


def run_game_of_life(W=100, H=50):
    game = GameOfLife(np.zeros((H, W), dtype=bool))
    controler = ControllerMidi(game, cellsize=20)
    controler.run()


def load_game_of_life(filepath: str):
    game = GameOfLife(filepath)
    controler = ControllerMidi(game, cellsize=20)
    controler.run()


if __name__ == "__main__":
    run_game_of_life()