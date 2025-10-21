import pygame
import sys
import math
import random

# Settings
WIDTH, HEIGHT = 900, 600
FPS = 60

# Flower color palettes
PALETTES = [
    [(255, 99, 132), (255, 205, 86), (75, 192, 192), (54, 162, 235)],
    [(255, 183, 197), (255, 223, 186), (186, 255, 201), (186, 225, 255)],
    [(255, 140, 0), (255, 215, 0), (0, 191, 255), (199, 21, 133)],
    [(144, 238, 144), (255, 182, 193), (221, 160, 221), (255, 250, 205)],
]

# Flower types
FLOWER_TYPES = ["daisy", "tulip", "aster", "sunflower"]

class Flower:
    def __init__(self, x, y, palette, ftype, t):
        self.x = x
        self.y = y
        self.palette = palette
        self.ftype = ftype
        self.t = t  # time of creation
        self.size = random.randint(30, 60)
        self.petal_count = random.randint(6, 12)
        self.angle = random.uniform(0, 2 * math.pi)

    def draw(self, surf, now):
        elapsed = now - self.t
        # Animate size and rotation
        size = self.size + 8 * math.sin(elapsed * 2)
        angle = self.angle + elapsed * 0.5
        cx, cy = self.x, self.y
        # Draw petals
        for i in range(self.petal_count):
            a = angle + i * 2 * math.pi / self.petal_count
            px = cx + math.cos(a) * size
            py = cy + math.sin(a) * size
            color = self.palette[i % len(self.palette)]
            if self.ftype == "daisy":
                pygame.draw.ellipse(surf, color, (px-12, py-18, 24, 36))
            elif self.ftype == "tulip":
                pygame.draw.polygon(surf, color, [
                    (cx, cy),
                    (px + 10, py),
                    (px, py + 20),
                    (px - 10, py)
                ])
            elif self.ftype == "aster":
                pygame.draw.line(surf, color, (cx, cy), (px, py), 8)
            elif self.ftype == "sunflower":
                pygame.draw.circle(surf, color, (int(px), int(py)), 14)
        # Center
        pygame.draw.circle(surf, (80, 60, 40), (int(cx), int(cy)), int(size * 0.3))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Color Garden - Interactive Art")
    clock = pygame.time.Clock()
    flowers = []
    palette_idx = 0
    ftype_idx = 0
    bg_hue = 0
    running = True
    while running:
        now = pygame.time.get_ticks() / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION and event.buttons[0]:
                mx, my = pygame.mouse.get_pos()
                flowers.append(Flower(mx, my, PALETTES[palette_idx], FLOWER_TYPES[ftype_idx], now))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    palette_idx = (palette_idx + 1) % len(PALETTES)
                if event.key == pygame.K_f:
                    ftype_idx = (ftype_idx + 1) % len(FLOWER_TYPES)
                if event.key == pygame.K_ESCAPE:
                    running = False
        # Animate background hue
        bg_hue = (bg_hue + 0.2) % 360
        color = pygame.Color(0)
        color.hsva = (bg_hue, 40, 100, 100)
        screen.fill(color)
        # Draw all flowers
        for flower in flowers:
            flower.draw(screen, now)
        # Instructions
        font = pygame.font.SysFont(None, 24)
        screen.blit(font.render("Click/drag to grow flowers. Press C to change colors, F to change flower type, ESC to quit.", True, (30,30,30)), (16, HEIGHT-32))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
