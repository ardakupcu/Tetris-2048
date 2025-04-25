################################################################################
#                                                                              #
# The main program of Tetris 2048 Base Code                                    #
#                                                                              #
################################################################################

import lib.stddraw as stddraw  # for creating an animation with user interactions
from lib.picture import Picture  # used for displaying an image on the game menu
from lib.color import Color  # used for coloring the game menu
import os  # the os module is used for file and directory operations
from game_grid import GameGrid  # the class for modeling the game grid
from tetromino import Tetromino  # the class for modeling the tetrominoes
import random  # used for creating tetrominoes with random types (shapes)
import time

# added by mustafa: flag to init window and scales only once
_initialized = False

# The main function where this program starts execution
def start():
   # set the dimensions of the game grid
   grid_h, grid_w = 20, 12

   # added by mustafa: initialize window and scales only on first call
   global _initialized
   if not _initialized:
      # set the size of the drawing canvas (the displayed window)
      stddraw.setCanvasSize(40 * grid_h, 40 * (grid_w + 6)) # added by mustafa
      # set the scale of the coordinate system for the drawing canvas
      stddraw.setXscale(-0.5, grid_w + 5.5) # added by mustafa
      stddraw.setYscale(-0.5, grid_h - 0.5) # added by mustafa
      _initialized = True # added by mustafa

   # set the game grid dimension values stored and used in the Tetromino class
   Tetromino.grid_height = grid_h
   Tetromino.grid_width = grid_w
   # create the game grid
   grid = GameGrid(grid_h, grid_w)
   # create the first tetromino to enter the game grid
   current_tetromino = create_tetromino()
   next_tetromino    = create_tetromino()
   grid.current_tetromino = current_tetromino

   # display a simple menu before opening the game
   display_game_menu(grid_h, grid_w)

   fall_interval = 0.3
   last_fall_time = time.time()
   paused = False # added by mustafa: pause flag

   # the main game loop
   while True:
      start_time = time.time()
      grid.display(next_tetromino)

      # check for any user interaction via the keyboard
      if stddraw.hasNextKeyTyped():
         key_typed = stddraw.nextKeyTyped()

         if key_typed == "p": # added by mustafa: pause toggle
            paused = not paused
            grid.paused = paused

         elif key_typed == "r": # added by mustafa: restart
            return start()

         elif not paused: # modified by mustafa: only move when not paused
            if key_typed == "left":
               current_tetromino.move("left", grid)
            elif key_typed == "right":
               current_tetromino.move("right", grid)
            elif key_typed == "down":
               current_tetromino.move("down", grid)
               last_fall_time = time.time()
            elif key_typed == "z":
               current_tetromino.rotate(grid)
            elif key_typed == "space":
               current_tetromino.hard_drop(grid)

         stddraw.clearKeysTyped()

      current_time = time.time()
      # modified by mustafa: only auto-drop when not paused
      if not paused and current_time - last_fall_time > fall_interval:
         moved = current_tetromino.move("down", grid)

         if not moved:
            tiles = current_tetromino.tile_matrix
            pos = current_tetromino.bottom_left_cell
            game_over, cleared = grid.update_grid(tiles, pos)

            grid.display()  # Görsel Olarak güncelleme

            # added by mustafa: check for win or game-over
            if game_over or grid.win:
               break

            current_tetromino = next_tetromino
            next_tetromino    = create_tetromino()
            grid.current_tetromino = current_tetromino

         last_fall_time = current_time

      elapsed = time.time() - start_time
      time.sleep(max(0, 1 / 60 - elapsed))  # 60 FPS

   # print a message on the console when the game is over
   print("Game over")

   # added by mustafa: end screen – restart with R
   while True:
      grid.display(next_tetromino)
      stddraw.show(50)
      if stddraw.hasNextKeyTyped() and stddraw.nextKeyTyped() == "r":
         stddraw.clearKeysTyped()
         return start()

# A function for creating random shaped tetrominoes to enter the game grid
def create_tetromino():
   tetromino_types = ['I', 'O', 'Z']
   random_index    = random.randint(0, len(tetromino_types) - 1)
   random_type     = tetromino_types[random_index]
   return Tetromino(random_type)

# A function for displaying a simple menu before starting the game
def display_game_menu(grid_height, grid_width):
   background_color = Color(42, 69, 99)
   button_color     = Color(25, 255, 228)
   text_color       = Color(31, 160, 239)

   stddraw.clear(background_color)
   current_dir = os.path.dirname(os.path.realpath(__file__))
   img_file    = current_dir + "/images/menu_image.png"
   img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7
   image_to_display = Picture(img_file)
   stddraw.picture(image_to_display, img_center_x, img_center_y)

   button_w, button_h = grid_width - 1.5, 2
   button_blc_x, button_blc_y = img_center_x - button_w / 2, 4
   stddraw.setPenColor(button_color)
   stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)

   stddraw.setFontFamily("Arial")
   stddraw.setFontSize(25)
   stddraw.setPenColor(text_color)
   stddraw.text(img_center_x, 5, "Click Here to Start the Game")

   while True:
      stddraw.show(50)
      if stddraw.mousePressed():
         mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
         if button_blc_x <= mouse_x <= button_blc_x + button_w and \
            button_blc_y <= mouse_y <= button_blc_y + button_h:
               break

if __name__ == '__main__':
   start()
