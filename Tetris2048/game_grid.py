import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing

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

      # show the resulting drawing with a pause duration = 250 ms
      stddraw.show(1)

   # A method for drawing the cells and the lines of the game grid
   def merge_tiles(self):
      merged = True
      while merged:
         merged = False
         for col in range(self.grid_width):
            row = 0
            while row < self.grid_height - 1:
               current = self.tile_matrix[row][col]
               above = self.tile_matrix[row + 1][col]
               if current is not None and above is not None:
                  if current.number == above.number:
                     # Merge and mark as merged
                     current.number *= 2
                     current.set_colors_by_value()
                     self.tile_matrix[row + 1][col] = None
                     merged = True

                     # Shift everything above down
                     for r in range(row + 2, self.grid_height):
                        self.tile_matrix[r - 1][col] = self.tile_matrix[r][col]
                     self.tile_matrix[self.grid_height - 1][col] = None

                     # Stay on same row to allow chain merge
                     continue
               row += 1

   def remove_floating_tiles_by_falling(self):
      visited = np.full((self.grid_height, self.grid_width), False)

      # Step 1: mark all grounded tiles using BFS
      from collections import deque
      queue = deque()

      for col in range(self.grid_width):
         if self.tile_matrix[0][col] is not None:
            queue.append((0, col))
            visited[0][col] = True

      while queue:
         row, col = queue.popleft()
         for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row + dy, col + dx
            if self.is_inside(r, c) and not visited[r][c] and self.tile_matrix[r][c] is not None:
               visited[r][c] = True
               queue.append((r, c))

      # Step 2: collect floating tiles (not visited)
      floating = []
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            if self.tile_matrix[row][col] is not None and not visited[row][col]:
               floating.append((row, col))

      if not floating:
         return

      # Step 3: fall each floating tile
      # Process bottom-up to avoid overwriting
      floating.sort(reverse=True)

      for row, col in floating:
         tile = self.tile_matrix[row][col]
         self.tile_matrix[row][col] = None
         new_row = row

         # Fall until grounded
         while (new_row > 0 and
                self.tile_matrix[new_row - 1][col] is None and
                not visited[new_row - 1][col]):
            new_row -= 1

         self.tile_matrix[new_row][col] = tile

   def draw_grid(self):
      # for each cell of the game grid
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            # if the current grid cell is occupied by a tile
            if self.tile_matrix[row][col] is not None:
               # draw this tile
               self.tile_matrix[row][col].draw(Point(col, row))
      # draw the inner lines of the game grid
      stddraw.setPenColor(self.line_color)
      stddraw.setPenRadius(self.line_thickness)
      # x and y ranges for the game grid
      start_x, end_x = -0.5, self.grid_width - 0.5
      start_y, end_y = -0.5, self.grid_height - 0.5
      for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
         stddraw.line(x, start_y, x, end_y)
      for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
         stddraw.line(start_x, y, end_x, y)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   # A method for drawing the boundaries around the game grid
   def draw_boundaries(self):
      # draw a bounding box around the game grid as a rectangle
      stddraw.setPenColor(self.boundary_color)  # using boundary_color
      # set the pen radius as box_thickness (half of this thickness is visible
      # for the bounding box as its lines lie on the boundaries of the canvas)
      stddraw.setPenRadius(self.box_thickness)
      # the coordinates of the bottom left corner of the game grid
      pos_x, pos_y = -0.5, -0.5
      stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   # A method used checking whether the grid cell with the given row and column
   # indexes is occupied by a tile or not (i.e., empty)
   def is_occupied(self, row, col):
      # considering the newly entered tetrominoes to the game grid that may
      # have tiles with position.y >= grid_height
      if not self.is_inside(row, col):
         return False  # the cell is not occupied as it is outside the grid
      # the cell is occupied by a tile if it is not None
      return self.tile_matrix[row][col] is not None

   # A method for checking whether the cell with the given row and col indexes
   # is inside the game grid or not
   def is_inside(self, row, col):
      if row < 0 or row >= self.grid_height:
         return False
      if col < 0 or col >= self.grid_width:
         return False
      return True

   # A method that locks the tiles of a landed tetromino on the grid checking
   # if the game is over due to having any tile above the topmost grid row.
   # (This method returns True when the game is over and False otherwise.)
   def update_grid(self, tiles_to_lock, blc_position):
      # necessary for the display method to stop displaying the tetromino
      self.current_tetromino = None
      # lock the tiles of the current tetromino (tiles_to_lock) on the grid
      n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
      for col in range(n_cols):
         for row in range(n_rows):
            # place each tile (occupied cell) onto the game grid
            if tiles_to_lock[row][col] is not None:
               # compute the position of the tile on the game grid
               pos = Point()
               pos.x = blc_position.x + col
               pos.y = blc_position.y + (n_rows - 1) - row
               if self.is_inside(pos.y, pos.x):
                  self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
               # the game is over if any placed tile is above the game grid
               else:
                  self.game_over = True
      # return the value of the game_over flag
      self.merge_tiles()
      self.remove_floating_tiles_by_falling()
      lines_cleared = self.clear_full_lines()
      return self.game_over, lines_cleared

   def clear_full_lines(self):
      lines_cleared = 0

      row = 0
      while row < self.grid_height:
         if all(self.tile_matrix[row][col] is not None for col in range(self.grid_width)):
            for r in range(row, self.grid_height - 1):
               for c in range(self.grid_width):
                  self.tile_matrix[r][c] = self.tile_matrix[r + 1][c]
            for c in range(self.grid_width):
               self.tile_matrix[self.grid_height - 1][c] = None
            lines_cleared += 1
         else:
            row += 1

      return lines_cleared

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

