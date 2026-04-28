import asyncio
import traceback
import pygame
from src.game import Game

async def main():
    try:
        await Game().run()
    except Exception:
        err = traceback.format_exc()
        print(err)
        try:
            if not pygame.get_init():
                pygame.init()
            screen = pygame.display.set_mode((600, 400))
            font = pygame.font.Font(None, 22)
            lines = err.splitlines()
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                screen.fill((0, 0, 0))
                for i, line in enumerate(lines[-16:]):
                    surf = font.render(line[:72], True, (255, 80, 80))
                    screen.blit(surf, (8, 8 + i * 22))
                pygame.display.flip()
                await asyncio.sleep(0)
        except Exception:
            pass

asyncio.run(main())
