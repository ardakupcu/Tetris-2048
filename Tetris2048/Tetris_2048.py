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

_initialized = False

def start():
    grid_h, grid_w = 20, 12
    global _initialized
    if not _initialized:
        stddraw.setCanvasSize(40 * grid_h, 40 * (grid_w + 6))
        stddraw.setXscale(-0.5, grid_w + 5.5)
        stddraw.setYscale(-0.5, grid_h - 0.5)
        _initialized = True

    Tetromino.grid_height = grid_h
    Tetromino.grid_width = grid_w

    grid = GameGrid(grid_h, grid_w)
    current_tetromino = create_tetromino()
    next_tetromino = create_tetromino()
    grid.current_tetromino = current_tetromino

    display_game_menu(grid_h, grid_w)

    fall_interval = 0.3
    last_fall_time = time.time()
    paused = False

    while True:
        start_time = time.time()
        grid.display(next_tetromino, paused)

        if stddraw.hasNextKeyTyped():
            key_typed = stddraw.nextKeyTyped()

            if key_typed == "p":
                paused = not paused

            elif key_typed == "r":
                return start()

            elif not paused:
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
        if not paused and current_time - last_fall_time > fall_interval:
            moved = current_tetromino.move("down", grid)

            if not moved:
                tiles = current_tetromino.tile_matrix
                pos = current_tetromino.bottom_left_cell
                game_over, _ = grid.update_grid(tiles, pos)

                if game_over or grid.win:
                    break

                current_tetromino = next_tetromino
                next_tetromino = create_tetromino()
                grid.current_tetromino = current_tetromino

            last_fall_time = current_time

        elapsed = time.time() - start_time
        time.sleep(max(0, 1 / 60 - elapsed))


    # Draw the end-game message only once
    grid.display(None)
    stddraw.setFontSize(32)
    end_msg = "YOU WIN!" if grid.win else "GAME OVER"
    stddraw.text(grid_w / 2, grid_h / 2, end_msg)
    stddraw.setFontSize(20)
    stddraw.text(grid_w / 2, grid_h / 2 - 2, "Press R to Restart")
    stddraw.show(0)  # Display the message once (without freezing)

    # Wait for user input to restart
    while True:
        time.sleep(0.05)  # Small sleep to avoid high CPU usage
        stddraw.show(0)   # Keep the window responsive
        if stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if key == "r":
                stddraw.clearKeysTyped()
                return start()


# A function for creating random shaped tetrominoes to enter the game grid
def create_tetromino():
   # the type (shape) of the tetromino is determined randomly
   tetromino_types = ['I', 'O', 'Z']
   random_index = random.randint(0, len(tetromino_types) - 1)
   random_type = tetromino_types[random_index]
   # create and return the tetromino
   tetromino = Tetromino(random_type)
   return tetromino

# A function for displaying a simple menu before starting the game
def display_game_menu(grid_height, grid_width):
   # the colors used for the menu
   background_color = Color(42, 69, 99)
   button_color = Color(25, 255, 228)
   text_color = Color(31, 160, 239)
   # clear the background drawing canvas to background_color
   stddraw.clear(background_color)
   # get the directory in which this python code file is placed
   current_dir = os.path.dirname(os.path.realpath(__file__))
   # compute the path of the image file
   img_file = current_dir + "/images/menu_image.png"
   # the coordinates to display the image centered horizontally
   img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7
   # the image is modeled by using the Picture class
   image_to_display = Picture(img_file)
   # add the image to the drawing canvas
   stddraw.picture(image_to_display, img_center_x, img_center_y)
   # the dimensions for the start game button
   button_w, button_h = grid_width - 1.5, 2
   # the coordinates of the bottom left corner for the start game button
   button_blc_x, button_blc_y = img_center_x - button_w / 2, 4
   # add the start game button as a filled rectangle
   stddraw.setPenColor(button_color)
   stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)
   # add the text on the start game button
   stddraw.setFontFamily("Arial")
   stddraw.setFontSize(25)
   stddraw.setPenColor(text_color)
   text_to_display = "Click Here to Start the Game"
   stddraw.text(img_center_x, 5, text_to_display)
   # the user interaction loop for the simple menu
   while True:
      # display the menu and wait for a short time (50 ms)
      stddraw.show(50)
      # check if the mouse has been left-clicked on the start game button
      if stddraw.mousePressed():
         # get the coordinates of the most recent location at which the mouse
         # has been left-clicked
         mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
         # check if these coordinates are inside the button
         if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
            if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
               break  # break the loop to end the method and start the game


# start() function is specified as the entry point (main function) from which
# the program starts execution
if __name__ == '__main__':
   start()
