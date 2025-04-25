import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing
from collections import deque  # added by mustafa: for floating tile removal

# A class for modeling the game grid
class GameGrid:
   # A constructor for creating the game grid based on the given arguments
   def __init__(self, grid_h, grid_w):
      # set the dimensions of the game grid as the given arguments
      self.grid_height = grid_h
      self.grid_width = grid_w
      # create a tile matrix to store the tiles locked on the game grid
      self.tile_matrix = np.full((grid_h, grid_w), None)
      # create the tetromino that is currently being moved on the game grid
      self.current_tetromino = None
      # the game_over flag shows whether the game is over or not
      self.game_over = False

      # added by mustafa: 2048 win status
      self.win = False
      # added by mustafa: pause status
      self.paused = False
      # added by mustafa: score tracking
      self.score = 0

      # set the color used for the empty grid cells
      self.empty_cell_color = Color(42, 69, 99)
      # set the colors used for the grid lines and the grid boundaries
      self.line_color = Color(0, 100, 200)
      self.boundary_color = Color(0, 100, 200)
      # thickness values used for the grid lines and the grid boundaries
      self.line_thickness = 0.002
      self.box_thickness = 10 * self.line_thickness

   # A method for displaying the game grid
   def display(self, next_tetromino=None):
      # clear the background to empty_cell_color
      stddraw.clear(self.empty_cell_color)
      # draw the game grid
      self.draw_grid()
      # draw the current/active tetromino if it is not None
      # (the case when the game grid is updated)
      if self.current_tetromino is not None:
         self.current_tetromino.draw()
      # draw a box around the game grid
      self.draw_boundaries()

      for x in range(self.grid_width, self.grid_width + 6):
         for y in range(self.grid_height):
            stddraw.setPenColor(self.empty_cell_color)
            stddraw.filledSquare(x, y, 0.5)

      if next_tetromino is not None:
         self.draw_next_tetromino(next_tetromino)

      # added by mustafa: score and status panel
      stddraw.setPenColor(self.line_color)
      stddraw.setFontSize(16)
      stddraw.text(self.grid_width + 3, self.grid_height - 1, "SCORE")
      stddraw.boldText(self.grid_width + 3, self.grid_height - 2.5, str(self.score))

      if self.paused:
         stddraw.boldText(self.grid_width/2, self.grid_height/2, "PAUSED")
      if self.win:
         stddraw.boldText(self.grid_width/2, self.grid_height/2, "YOU WIN!")
      if self.game_over and not self.win:
         stddraw.boldText(self.grid_width/2, self.grid_height/2, "GAME OVER")
      # end added by mustafa

      # show the resulting drawing with a pause duration = 1 ms
      stddraw.show(1)

   # A method for merging tiles column-wise (2048 chaining)
   def merge_tiles(self): # added by mustafa: merge_tiles method
      gained = 0
      for col in range(self.grid_width):
         row = 0
         while row < self.grid_height - 1:
            current = self.tile_matrix[row][col]
            above  = self.tile_matrix[row+1][col]
            if current and above and current.number == above.number:
               # merge the two tiles
               current.number *= 2
               current.set_colors_by_value() # modified by mustafa: update color after merge
               gained += current.number
               if current.number == 2048:
                  self.win = True # added by mustafa: set win on reaching 2048
               # remove and shift down
               self.tile_matrix[row+1][col] = None
               for r in range(row+2, self.grid_height):
                  self.tile_matrix[r-1][col] = self.tile_matrix[r][col]
               self.tile_matrix[self.grid_height-1][col] = None
               # stay on same row for chain merges
               continue
            row += 1
      return gained # added by mustafa: return total merge gain

   # A method for clearing full horizontal lines
   def clear_full_lines(self): # modified by mustafa: clear_full_lines signature and return
      lines_cleared = 0
      line_gain     = 0
      row = 0
      while row < self.grid_height:
         if all(self.tile_matrix[row][c] is not None for c in range(self.grid_width)):
            # add line-clear gain
            line_gain += sum(self.tile_matrix[row][c].number for c in range(self.grid_width))
            # shift grid down
            for r in range(row, self.grid_height - 1):
               for c in range(self.grid_width):
                  self.tile_matrix[r][c] = self.tile_matrix[r+1][c]
            for c in range(self.grid_width):
               self.tile_matrix[self.grid_height - 1][c] = None
            lines_cleared += 1
         else:
            row += 1
      return lines_cleared, line_gain # modified by mustafa: return lines cleared and gain

   # A method for deleting floating tiles and adding their value
   def remove_floating_tiles(self): # added by mustafa: remove_floating_tiles method
      visited = np.full((self.grid_height, self.grid_width), False)
      q = deque([(0, c) for c in range(self.grid_width) if self.tile_matrix[0][c]])
      while q:
         r, c = q.popleft()
         visited[r][c] = True
         for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.grid_height and 0 <= nc < self.grid_width:
               if self.tile_matrix[nr][nc] and not visited[nr][nc]:
                  q.append((nr, nc))

      floating_gain = 0
      for r in range(self.grid_height):
         for c in range(self.grid_width):
            if self.tile_matrix[r][c] and not visited[r][c]:
               floating_gain += self.tile_matrix[r][c].number
               self.tile_matrix[r][c] = None
      return floating_gain # added by mustafa: return total floating tiles gain

   # A method for drawing the cells and the lines of the game grid
   def draw_grid(self):
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            if self.tile_matrix[row][col] is not None:
               self.tile_matrix[row][col].draw(Point(col, row))
      stddraw.setPenColor(self.line_color)
      stddraw.setPenRadius(self.line_thickness)
      start_x, end_x = -0.5, self.grid_width - 0.5
      start_y, end_y = -0.5, self.grid_height - 0.5
      for x in np.arange(start_x + 1, end_x, 1):
         stddraw.line(x, start_y, x, end_y)
      for y in np.arange(start_y + 1, end_y, 1):
         stddraw.line(start_x, y, end_x, y)
      stddraw.setPenRadius()

   # A method for drawing the boundaries around the game grid
   def draw_boundaries(self):
      stddraw.setPenColor(self.boundary_color)
      stddraw.setPenRadius(self.box_thickness)
      pos_x, pos_y = -0.5, -0.5
      stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
      stddraw.setPenRadius()

   # Check if a cell is occupied
   def is_occupied(self, row, col):
      if not self.is_inside(row, col):
         return False
      return self.tile_matrix[row][col] is not None

   # Check if a cell is inside the grid
   def is_inside(self, row, col):
      if row < 0 or row >= self.grid_height: return False
      if col < 0 or col >= self.grid_width:  return False
      return True

   # Lock tiles of a landed tetromino, then handle scoring
   def update_grid(self, tiles_to_lock, blc_position): # modified by mustafa: update_grid signature
      self.current_tetromino = None
      n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
      for col in range(n_cols):
         for row in range(n_rows):
            if tiles_to_lock[row][col] is not None:
               pos = Point()
               pos.x = blc_position.x + col
               pos.y = blc_position.y + (n_rows - 1) - row
               if self.is_inside(pos.y, pos.x):
                  self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
               else:
                  self.game_over = True

      # Merge → Clear Lines → Remove Floating, in that order
      self.score += self.merge_tiles() # added by mustafa: add merge gain
      lines_cleared, line_gain = self.clear_full_lines() # added by mustafa: add line-clear gain
      self.score += line_gain # added by mustafa: add line gain
      self.score += self.remove_floating_tiles() # added by mustafa: add floating-tile gain

      return self.game_over, lines_cleared # modified by mustafa: update_grid return

   # Draw the next tetromino preview
   def draw_next_tetromino(self, tetromino):
      from point import Point
      offset_x = self.grid_width + 2
      offset_y = self.grid_height - 5

      tile_matrix = tetromino.tile_matrix
      n_rows = len(tile_matrix)
      n_cols = len(tile_matrix[0])

      for row in range(n_rows):
         for col in range(n_cols):
            tile = tile_matrix[row][col]
            if tile is not None:
               position = Point(offset_x + col, offset_y - row)
               tile.draw(position, length=1, is_preview=False)

      stddraw.setPenColor(self.line_color)
      stddraw.setFontSize(16)
      stddraw.text(offset_x + 1, offset_y + 3, "Next")
