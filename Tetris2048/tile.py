import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color  # used for coloring the tiles
import random
# A class for modeling numbered tiles as in 2048
class Tile:
   # Class variables shared among all Tile objects
   # ---------------------------------------------------------------------------
   # the value of the boundary thickness (for the boxes around the tiles)
   boundary_thickness = 0.004
   # font family and font size used for displaying the tile number
   font_family, font_size = "Arial", 14

   # A constructor that creates a tile with 2 as the number on it
   def __init__(self, number=None):
      # Accept 2 or 4 as number; default to random
      self.number = number if number is not None else random.choice([2, 4]) #Tetrominoları 2 ve 4 sayılı bloklardan oluşturma
      self.set_colors_by_value()

   def set_colors_by_value(self):
      from lib.color import Color

      color_map = {                           #Sayıya Göre Renk Ataması
         2: Color(238, 228, 218),
         4: Color(237, 224, 200),
         8: Color(242, 177, 121),
         16: Color(245, 149, 99),
         32: Color(246, 124, 95),
         64: Color(246, 94, 59),
         128: Color(237, 207, 114),
         256: Color(237, 204, 97),
         512: Color(237, 200, 80),
         1024: Color(237, 197, 63),
         2048: Color(237, 194, 46)
      }

      # Default if value not in map
      self.background_color = color_map.get(self.number, Color(60, 58, 50))
      self.foreground_color = Color(119, 110, 101) if self.number <= 4 else Color(255, 255, 255)
      self.box_color = Color(187, 173, 160)

   # A method for drawing this tile at a given position with a given length
   def draw(self, position, length=1, is_preview=False):  # length defaults to 1
      # draw the tile as a filled square
      stddraw.setPenColor(self.background_color)
      stddraw.filledSquare(position.x, position.y, length / 2)
      # draw the bounding box around the tile as a square
      stddraw.setPenColor(self.box_color)
      stddraw.setPenRadius(Tile.boundary_thickness)
      stddraw.square(position.x, position.y, length / 2)
      stddraw.setPenRadius()  # reset the pen radius to its default value
      # draw the number on the tile
      if not is_preview:
         stddraw.setPenColor(self.foreground_color)
         stddraw.setFontFamily(Tile.font_family)
         stddraw.setFontSize(Tile.font_size)
         stddraw.text(position.x, position.y, str(self.number))
