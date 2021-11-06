import pygame
import time

# Margins
MARGIN_LEFT = 230
MARGIN_TOP = 150

# WINDOW SIZE
WIDTH = 1750
HEIGHT = 1000

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (38, 150, 37)
DARK_GREEN = (10, 90, 7)
RED = (203, 16, 16)
BLUE = (44, 109, 238)

pygame.init()

# Setting up the screen and background
# Types of fonts to be used
small_font = pygame.font.Font(None, 32)
large_font = pygame.font.Font(None, 50)

screen = None

def set_up_graphics():
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(GREEN)

    # Setting up caption
    pygame.display.set_caption("Scum")
    pygame.display.update()

def translate_for_graphics(action):
    res = []
    for a in action:
        card = str(a)
        num = ""
        suit = ""
        if card[0] not in ['Q', 'K', 'J', '1', 'A']:
            num = card[0]
        elif card[0] == 'Q':
            num = 'queen'
        elif card[0] == 'K':
            num = 'king'
        elif card[0] == 'J':
            num = 'jack'
        else:
            num = 'ace'
        
        if card[1] == 'C':
            suit = 'clubs'
        elif card[1] == 'D':
            suit = 'diamonds'
        elif card[1] == 'S':
            suit = 'spades'
        else:
            suit = 'hearts'
        
        filename = num + "_of_" + suit + ".png"
        res.append(filename)
    return res

def get_speed(tick_speed):
    time_sleep = []
    if tick_speed == 1:
        time_sleep = [1, 2, 6]
    elif tick_speed == 2:
        time_sleep = [.5, 1, 5]
    elif tick_speed == 3:
        time_sleep = [.25, .75, 4]
    elif tick_speed == 4:
        time_sleep = [.15, .5, 2]
    elif tick_speed == 5:
        time_sleep = [.05, .125, 2]

    return time_sleep
        
def draw_graphics(round, player, action, gamestate):
    global screen
    pygame.event.get()

    time_arr = get_speed(gamestate.tick_speed)
    time_sleep = time_arr[0]

    # Draw other player's indicator
    pygame.draw.rect(screen, DARK_GREEN, (0,0,WIDTH,350))
    pygame.draw.line(screen, RED, (0, 350), (WIDTH, 350))
    pygame.draw.line(screen, BLACK, (0, 351), (WIDTH, 351))
    pygame.draw.line(screen, BLACK, (0, 352), (WIDTH, 352))
    pygame.draw.line(screen, BLACK, (0, 353), (WIDTH, 353))
    pygame.draw.line(screen, RED, (0, 354), (WIDTH, 354))


    text = small_font.render("Overview of Players", True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = (WIDTH//2, 50)
    screen.blit(text, text_rect)

    scum = -1
    if gamestate.n - len(gamestate.out) == 1:
        for i in range(gamestate.n):
            if i not in gamestate.out:
                scum = i
                time_sleep = time_arr[2]
                break
    
    offset = 0
    start = WIDTH//2 - 85 * (gamestate.n // 2)
    for i in gamestate.play_order:
        c = pygame.image.load(r'./' + 'avatar.jpg')
        c = pygame.transform.scale(c , (75,75))
        screen.blit(c, (start-30+offset, 155))

        num_text = small_font.render(str(i+1), True, BLACK)
        num_text_rect = num_text.get_rect()
        num_text_rect.center = (start+10+offset, 185)
        screen.blit(num_text, num_text_rect)

        play_order_text = small_font.render("Play Order:", True, WHITE)
        play_order_rect = play_order_text.get_rect()
        play_order_rect.center = (start-150, 185)
        screen.blit(play_order_text, play_order_rect)

        rounds_won_text = small_font.render("Rounds Won:", True, WHITE)
        rounds_won_text_rect = rounds_won_text.get_rect()
        rounds_won_text_rect.center = (start-150, 250)
        screen.blit(rounds_won_text, rounds_won_text_rect)

        hands_rem_text = small_font.render("Cards Remaining:", True, WHITE)
        hands_rem_text_rect = hands_rem_text.get_rect()
        hands_rem_text_rect.center = (start-150, 300)
        screen.blit(hands_rem_text, hands_rem_text_rect)

        if i in gamestate.out:
            place = large_font.render(str(gamestate.out.index(i)+1), True, BLUE)
            place_rect = place.get_rect()
            place_rect.center = (start+10+offset, 135)
            screen.blit(place, place_rect)
        elif scum != -1 and i == scum:
            place = large_font.render(str(len(gamestate.out)+1), True, RED)
            place_rect = place.get_rect()
            place_rect.center = (start+10+offset, 135)
            screen.blit(place, place_rect)

        rounds = large_font.render(str(gamestate.rounds_won[i]), True, WHITE)
        rounds_rect = rounds.get_rect()
        rounds_rect.center = (start+10+offset, 250)
        screen.blit(rounds, rounds_rect)

        cards = large_font.render(str(len(gamestate.hands[i].cards)), True, WHITE)
        cards_rect = rounds.get_rect()
        cards_rect.center = (start+10+offset, 300)
        screen.blit(cards, cards_rect)

        offset+=95

    # Draw the table with cards
    round_text = small_font.render("Round "+str(round+1), True, BLACK)
    round_text_rect = round_text.get_rect()
    round_text_rect.center = (WIDTH//2, HEIGHT//2 - 120)
    screen.blit(round_text, round_text_rect)

    player_text = small_font.render("Player "+str(player+1), True, BLACK)
    player_text_rect = player_text.get_rect()
    player_text_rect.center = (WIDTH//2, HEIGHT//2 - 90)
    screen.blit(player_text, player_text_rect)

    ac = ""
    if action == 'Pass':
        ac = "Passed"
    elif action == "WIN":
        ac = "Won this turn"
        time_sleep = time_arr[1]
    else:
        ac = ' & '.join([str(a) for a in action])

    hand_text = small_font.render("Action: " + ac, True, BLACK)
    hand_text_rect = hand_text.get_rect()
    hand_text_rect.center = (WIDTH//2, HEIGHT//2 - 60)
    screen.blit(hand_text, hand_text_rect)

    turn_text = small_font.render("Turn: " + str(gamestate.turn_count), True, BLACK)
    turn_text_rect = turn_text.get_rect()
    turn_text_rect.center = (WIDTH//2, HEIGHT//2 - 30)
    screen.blit(turn_text, turn_text_rect)

    if action == "Pass" or action == "WIN":
        action = gamestate.last_action

    offset = 0
    if action != "Pass":
        start = WIDTH//2 - 115 * (len(action) // 2)
        for file in translate_for_graphics(action):
            c = pygame.image.load(r'./cards/' + file)
            c = pygame.transform.scale(c , (100,160))
            screen.blit(c, (start+offset, HEIGHT//2 + 30))
            offset+=120

    gamestate.last_action = action


    # Draw Player One's Hand
    pygame.draw.line(screen, RED, (0, 750), (WIDTH, 750))
    pygame.draw.line(screen, BLACK, (0, 751), (WIDTH, 751))
    pygame.draw.line(screen, BLACK, (0, 752), (WIDTH, 752))
    pygame.draw.line(screen, BLACK, (0, 753), (WIDTH, 753))
    pygame.draw.line(screen, RED, (0, 754), (WIDTH, 754))

    pygame.draw.rect(screen, DARK_GREEN, (0,754,WIDTH,1000))

    player_one_text = small_font.render("Player One's Hand: ", True, WHITE)
    player_one_rect = player_one_text.get_rect()
    player_one_rect.center = (WIDTH//2, HEIGHT//2 + 300)
    screen.blit(player_one_text, player_one_rect)

    offset = 0
    start = WIDTH//2 - 75 * (len(gamestate.hands[0].cards) // 2)
    for file in translate_for_graphics(gamestate.hands[0].cards):
        c = pygame.image.load(r'./cards/' + file)
        c = pygame.transform.scale(c , (70,112))
        screen.blit(c, (start+offset, HEIGHT//2 + 350))
        offset+=80


    if player not in gamestate.out or scum != -1:
        pygame.display.update()
        time.sleep(time_sleep)
    screen.fill(GREEN)

def quit_pygame():
    pygame.quit()