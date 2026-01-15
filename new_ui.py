import sys
import math
import pygame

import board as board_mod
import game as game_mod
import minimax as minimax_mod


BOARD_DIM = 5                 
WINDOW_SIZE = 1000             
LINE_WIDTH = 6
PADDING = 20                 
FPS = 60

BG_COLOR = (245, 245, 245)
GRID_COLOR = (50, 50, 50)
P1_COLOR = (40, 120, 220)     
P2_COLOR = (220, 60, 60)      
TEXT_COLOR = (20, 20, 20)
OVERLAY_BG = (255, 255, 255)

def draw_grid(surface, n, cell):
    for i in range(1, n):
        # vertical
        x = i * cell
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, n*cell), LINE_WIDTH)
        # horizontal
        y = i * cell
        pygame.draw.line(surface, GRID_COLOR, (0, y), (n*cell, y), LINE_WIDTH)

def draw_pieces(surface, board_array, cell):
    n = board_array.shape[0]
    for r in range(n):
        for c in range(n):
            piece = board_array[r][c]
            cx = c * cell + cell // 2
            cy = r * cell + cell // 2
            half = cell // 2 - PADDING
            if piece == 1:

                pygame.draw.circle(surface, P1_COLOR, (cx, cy), half, LINE_WIDTH)
            elif piece == 2:

                pygame.draw.line(surface, P2_COLOR, (cx - half, cy - half), (cx + half, cy + half), LINE_WIDTH)
                pygame.draw.line(surface, P2_COLOR, (cx + half, cy - half), (cx - half, cy + half), LINE_WIDTH)

def show_message(surface, text, subtext=None):
    w, h = surface.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 210))
    surface.blit(overlay, (0, 0))

    font = pygame.font.SysFont(None, 64)
    font2 = pygame.font.SysFont(None, 32)
    t_surf = font.render(text, True, TEXT_COLOR)
    t_rect = t_surf.get_rect(center=(w//2, h//2 - 20))
    surface.blit(t_surf, t_rect)

    if subtext:
        st_surf = font2.render(subtext, True, TEXT_COLOR)
        st_rect = st_surf.get_rect(center=(w//2, h//2 + 30))
        surface.blit(st_surf, st_rect)

def reset_game(dimension):

    g = game_mod.Game(dimension)
    current_turn_piece = 1
    return g, current_turn_piece

def ai_move(game_obj:game_mod):
    """AI places piece=2 and returns (i, j) of the move, or None."""
    i = j = None
    try:
        res = minimax_mod.best_move(game_obj.current_board, 2)
        if isinstance(res, tuple) and len(res) >= 2:
            i, j = int(res[0]), int(res[1])
    except Exception:
        i = j = None


    if i is None or j is None or game_obj.current_board.board_array[i][j] != 0:
        n = game_obj.current_board.dimension
        found = False
        for r in range(n):
            for c in range(n):
                if game_obj.current_board.board_array[r][c] == 0:
                    i, j = r, c
                    found = True
                    break
            if found:
                break

    if i is not None and j is not None and game_obj.current_board.board_array[i][j] == 0:
        game_obj.current_board.change_state(i, j, 2)
        return (i, j)
    return None

def human_try_place(game_obj, pos, cell):
    """Place piece=1 for human and return (r, c) if placed, else None."""
    x, y = pos
    r = y // cell
    c = x // cell
    n = game_obj.current_board.dimension
    if 0 <= r < n and 0 <= c < n and game_obj.current_board.board_array[r][c] == 0:
        game_obj.current_board.change_state(r, c, 1)
        return (r, c)
    return None

def main():
    pygame.init()
    pygame.display.set_caption("Your Minimax Board (Human vs AI)")
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    clock = pygame.time.Clock()
    cell = WINDOW_SIZE // BOARD_DIM

    game_obj, turn_piece = reset_game(BOARD_DIM)

    game_over = False
    outcome_text = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    game_obj, turn_piece = reset_game(BOARD_DIM)
                    game_over = False
                    outcome_text = None

            if not game_over and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn_piece == 1:
                    move = human_try_place(game_obj, pygame.mouse.get_pos(), cell)
                    if move:
                        hr, hc = move

                        if game_obj.current_board.check_win_from(hr, hc, 1):
                            game_over = True
                            outcome_text = "You (Player 1) win!"
                        elif game_obj.current_board.check_draw():
                            game_over = True
                            outcome_text = "Draw!"
                        else:

                            turn_piece = 2
                            ai_mv = ai_move(game_obj)
                            if ai_mv:
                                ar, ac = ai_mv

                                if game_obj.current_board.check_win_from(ar, ac, 2):
                                    game_over = True
                                    outcome_text = "AI (Player 2) wins!"
                                elif game_obj.current_board.check_draw():
                                    game_over = True
                                    outcome_text = "Draw!"
                                else:

                                    turn_piece = 1


        screen.fill(BG_COLOR)
        draw_grid(screen, BOARD_DIM, cell)
        draw_pieces(screen, game_obj.current_board.board_array, cell)

        if game_over:
            show_message(screen, outcome_text, "Press R to restart, Esc to quit.")

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
