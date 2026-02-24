import pygame, random, math

# constants
FPS = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BALL_SPEED = 500
MAX_SCORE = 5
COLOUR_BG = "white"

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y, w, h):
        self.score = 0
        self.colour = "black"
        self.speed = BALL_SPEED
        self.width = w
        self.height = h
        self.orig = (x - w/2, y - h/2,)
        self.rect = pygame.Rect(x - w/2, y - h/2, w, h)

    def up(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.y < 0:
            self.rect.y = 0
    
    def down(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.y > SCREEN_HEIGHT - self.height:
            self.rect.y = SCREEN_HEIGHT - self.height

    def reset(self):
        self.rect.x = self.orig[0]
        self.rect.y = self.orig[1]

    def draw(self):
        pygame.draw.rect(screen, self.colour, self.rect)

class Ball:
    def __init__(self, x, y, r):
        self.colour = "black"
        self.speed = BALL_SPEED
        self.radius = r
        self.orig = (x, y)
        self.rect = pygame.Rect(x - r, y - r, 2 * r, 2 * r)
        self.vel = pygame.Vector2(random.random() - 0.5, random.random() - 0.5)
        self.vel.scale_to_length(self.speed)

    def update(self, dt):
        self.rect.x += self.vel.x * dt
        self.rect.y += self.vel.y * dt

        # wall hit
        if self.rect.y < 0:
            self.rect.y = -self.rect.y
            self.vel.y *= -1
        if self.rect.y + 2 * self.radius > SCREEN_HEIGHT:
            self.rect.y = 2 * SCREEN_HEIGHT - self.rect.y - 4 * self.radius
            self.vel.y *= -1

        # bat hit
        if self.rect.colliderect(players[0].rect):
            if self.rect.center[0] - players[0].rect.center[0] == 0:
                self.vel.y *= -1
            else:
                crit = math.atan(players[0].height / players[0].width)
                angle = math.atan((self.rect.center[1] - players[0].rect.center[1]) / (self.rect.center[0] - players[0].rect.center[0]))
                if abs(angle) < crit:
                    self.vel.x = abs(self.vel.x)
                else:
                    self.vel.y *= -1
        if self.rect.colliderect(players[1].rect):
            if self.rect.center[0] - players[1].rect.center[0] == 0:
                self.vel.y *= -1
            else:
                crit = math.atan(players[1].height / players[1].width)
                angle = math.atan((self.rect.center[1] - players[1].rect.center[1]) / (self.rect.center[0] - players[1].rect.center[0]))
                if abs(angle) < crit:
                    self.vel.x = -abs(self.vel.x)
                else:
                    self.vel.y *= -1

        # score
        if self.rect.x < 0:
            return 1
        if self.rect.x + 2 * self.radius > SCREEN_WIDTH:
            return 0
        return -1

    def reset(self):
        self.rect.x = self.orig[0]
        self.rect.y = self.orig[1]
        self.vel.update(random.random() - 0.5, random.random() - 0.5)
        self.vel.scale_to_length(self.speed)
    
    def draw(self):
        pygame.draw.circle(screen, self.colour, self.rect.center, self.radius)

players = [Player(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.5, SCREEN_WIDTH * 0.04, SCREEN_HEIGHT * 0.25),
           Player(SCREEN_WIDTH * 0.9, SCREEN_HEIGHT * 0.5, SCREEN_WIDTH * 0.04, SCREEN_HEIGHT * 0.25)]
ball = Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH * 0.02)

def draw():
    screen.fill(COLOUR_BG)
    players[0].draw()
    players[1].draw()
    ball.draw()
    if pygame.font:
        font = pygame.font.Font(None, 64)
        text = font.render(f"{players[0].score} - {players[1].score}", True, "black")
        pos = text.get_rect(centerx=screen.get_width()/2, y=10)
        screen.blit(text, pos)

def update(dt):
    keys = pygame.key.get_pressed()

    # bat one
    if keys[pygame.K_1]:
        players[0].up(dt)
    if keys[pygame.K_2]:
        players[0].down(dt)

    # bat two
    if keys[pygame.K_9]:
        players[1].up(dt)
    if keys[pygame.K_0]:
        players[1].down(dt)

    # ball
    status = ball.update(dt)
    if status != -1:
        ball.reset()
        players[0].reset()
        players[1].reset()
        players[status].score += 1
        if players[status].score == MAX_SCORE:
            print(f"Player {status + 1} wins!")
            return status
    return -1

def run():
    running = True
    dt = 0

    # game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw()
        if update(dt) != -1:
            running = False

        pygame.display.flip()
        dt = clock.tick(FPS) * 0.001

    pygame.quit()

if __name__ == "__main__":
    run()