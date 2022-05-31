import pytmx
import pygame as pg


# HANDLES THE INTIAL SETUP AND STORAGE OF THE LEVEL TMX FILE FROM TILED
class TiledMap:
	def __init__(self, file_name):
		tm = pytmx.load_pygame(file_name, pixelalpha = True)
		self.width = tm.width * tm.tilewidth
		self.height = tm.height * tm.tileheight
		self.tmx_data = tm
		self.obstacles = []

	def render(self, surface):
		ti = self.tmx_data.get_tile_image_by_gid
		for layer in self.tmx_data.visible_layers:
			if isinstance(layer, pytmx.TiledTileLayer):
				for x, y, gid in layer:
					tile = ti(gid)
					if tile:
						surface.blit(tile, (x*self.tmx_data.tileheight, 
											y * self.tmx_data.tilewidth))
						if layer.name == "scenery":
							rect = pg.Rect(x*self.tmx_data.tilewidth, y*self.tmx_data.tileheight, self.tmx_data.tilewidth, self.tmx_data.tileheight)
							self.obstacles.append(rect)

	def make_map(self):
		temp_surface = pg.Surface((self.width, self.height))
		self.render(temp_surface)
		return temp_surface
