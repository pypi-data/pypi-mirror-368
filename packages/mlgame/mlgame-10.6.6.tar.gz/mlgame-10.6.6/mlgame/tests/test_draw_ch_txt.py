import pygame
import os
# Initialize pygame
def test_draw_ch_txt():
    pygame.init()

    # Screen setup
    WIDTH, HEIGHT = 600, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame Chinese Text Example")

    # Load a Chinese font (Ensure this font file exists)
    font_path = os.path.join(os.path.dirname(__file__),"..","assets", "NotoSansTC-Regular.ttf")  # Replace with your own Chinese TTF/OTF font
    font = pygame.font.Font(font_path, 36)  # Load font with size 36

    # Render text
    text_surface = font.render("你好，Pygame!", True, (0, 0, 0))  # Black color

    # Game loop
    running = True
    while running:
        screen.fill((255, 255, 255))  # White background
        screen.blit(text_surface, (100, 150))  # Draw text on screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()