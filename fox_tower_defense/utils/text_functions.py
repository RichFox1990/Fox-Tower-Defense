from utils.SETTINGS import COLOURS
import pygame as pg


# Function found online to draw hollow text (no credit to me here)
def hollow_text(font, message, fontcolor):
    notcolor = [c ^ 0xFF for c in fontcolor]
    base = font.render(message, 0, fontcolor, notcolor)
    size = base.get_width() + 2, base.get_height() + 2
    img = pg.Surface(size, 16)
    img.fill(notcolor)
    base.set_colorkey(0)
    img.blit(base, (0, 0))
    img.blit(base, (2, 0))
    img.blit(base, (0, 2))
    img.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, notcolor)
    img.blit(base, (1, 1))
    img.set_colorkey(notcolor)
    return img


# Function found online to outline text (no credit to me here)
def outline_text(font, message, fontcolor, outlinecolor):
    base = font.render(message, 0, fontcolor)
    outline = hollow_text(font, message, outlinecolor)
    img = pg.Surface(outline.get_size(), 16)
    img.fill(COLOURS["magenta"])
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(COLOURS["magenta"])
    return img
