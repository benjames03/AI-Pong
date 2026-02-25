import pygame, random, math, time

# constants
FPS = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
INIT_SPEED = 600
MAX_SPEED = 3000
MAX_SCORE = 5
FRICTION = 1
RESTITUTION = 15
COLOUR_BG = "white"
BINDINGS = ((pygame.K_1, pygame.K_2), (pygame.K_9, pygame.K_0))

class Player:
    def __init__(self, x, y, w, h, up, down):
        self.score = 0
        self.up = up
        self.down = down
        self.colour = "black"
        self.max_speed = INIT_SPEED
        self.width = w
        self.height = h
        self.orig = (x - w/2, y - h/2,)
        self.rect = pygame.Rect(x - w/2, y - h/2, w, h)
        self.velocity = 0

    def move(self, dt, a):
        self.velocity += a * dt * 10000
        if self.velocity < -self.max_speed:
            self.velocity = -self.max_speed
        if self.velocity > self.max_speed:
            self.velocity = self.max_speed

        self.rect.y += self.velocity * dt
        if self.rect.y < 0:
            self.rect.y = 0
            self.velocity = 0
        if self.rect.y > SCREEN_HEIGHT - self.height:
            self.rect.y = SCREEN_HEIGHT - self.height
            self.velocity = 0

    def reset(self):
        self.rect.x = self.orig[0]
        self.rect.y = self.orig[1]
        self.velocity = 0

    def draw(self):
        pygame.draw.rect(screen, self.colour, self.rect)

class Ball:
    def __init__(self, x, y, r):
        self.colour = "black"
        self.speed = INIT_SPEED
        self.max_speed = MAX_SPEED
        self.radius = r
        self.orig = (x, y)
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(2 * random.random() - 1, random.random() - 0.5)
        self.vel.scale_to_length(self.speed)

    def update(self, dt):
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt

        # wall hit
        if self.pos.y - self.radius < 0:
            self.pos.y = 2 * self.radius - self.pos.y
            self.vel.y *= -1
        if self.pos.y + self.radius > SCREEN_HEIGHT:
            self.pos.y = 2 * SCREEN_HEIGHT - self.pos.y - 2 * self.radius
            self.vel.y *= -1

        # bat hit
        for player in players:
            cx = max(player.rect.left, min(self.pos.x, player.rect.right))
            cy = max(player.rect.top, min(self.pos.y, player.rect.bottom))
            
            dx = self.pos.x - cx
            dy = self.pos.y - cy
            
            if (dx**2 + dy**2) < self.radius**2:
                if abs(dx) > abs(dy):
                    v = self.vel.magnitude()
                    self.vel.x *= -1
                    self.vel.y += player.velocity * FRICTION
                    self.vel.scale_to_length(min(self.max_speed, v + abs(player.velocity) * RESTITUTION / player.max_speed))
                    self.pos.x = cx + (self.radius if dx > 0 else -self.radius)
                else:
                    self.vel.y *= -1
                    self.pos.y = cy + (self.radius if dy > 0 else -self.radius)

        # score
        if self.pos.x - self.radius < 0:
            return 1
        if self.pos.x + self.radius > SCREEN_WIDTH:
            return 0
        return -1

    def reset(self):
        self.pos.x = self.orig[0]
        self.pos.y = self.orig[1]
        self.vel.update(2 * random.random() - 1, random.random() - 0.5)
        self.vel.scale_to_length(self.speed)
    
    def draw(self):
        pygame.draw.circle(screen, self.colour, self.pos, self.radius)

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

    # bats
    for player in players:
        if keys[player.up]:
            player.move(dt, -1)
        if keys[player.down]:
            player.move(dt, 1)
        if not keys[player.up] and not keys[player.down]:
            player.velocity = 0

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
    elapsed = 0

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
        elapsed += dt

    pygame.quit()

if __name__ == "__main__":
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    players = [Player(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.5, SCREEN_WIDTH * 0.04, SCREEN_HEIGHT * 0.25, pygame.K_1, pygame.K_2),
               Player(SCREEN_WIDTH * 0.9, SCREEN_HEIGHT * 0.5, SCREEN_WIDTH * 0.04, SCREEN_HEIGHT * 0.25, pygame.K_9, pygame.K_0)]
    ball = Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH * 0.02)

    run()