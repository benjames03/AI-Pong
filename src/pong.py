import pygame, random

WIDTH, HEIGHT = 1280, 720

class Player:
    def __init__(self, x, y, w, h, v, up, down):
        self.score = 0
        self.up = up
        self.down = down
        self.max_speed = v
        self.width = w
        self.height = h
        self.orig = (x - w/2, y - h/2)
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
        if self.rect.y > HEIGHT - self.height:
            self.rect.y = HEIGHT - self.height
            self.velocity = 0

    def reset(self):
        self.rect.x = self.orig[0]
        self.rect.y = self.orig[1]
        self.velocity = 0

class Ball:
    def __init__(self, x, y, r, vi, vm):
        self.colour = "black"
        self.speed = vi
        self.max_speed = vm
        self.radius = r
        self.orig = pygame.Vector2(x, y)
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(2 * random.random() - 1, random.random() - 0.5)
        self.vel.scale_to_length(self.speed)

    def move(self, dt):
        self.pos += self.vel * dt

        # wall hit
        if self.pos.y - self.radius < 0:
            self.pos.y = 2 * self.radius - self.pos.y
            self.vel.y *= -1
        if self.pos.y + self.radius > HEIGHT:
            self.pos.y = 2 * HEIGHT - self.pos.y - 2 * self.radius
            self.vel.y *= -1

        # score
        if self.pos.x - self.radius < 0:
            return 1
        if self.pos.x + self.radius > WIDTH:
            return 0
        return -1

    def reset(self):
        self.pos = self.orig.copy()
        self.vel.update(2 * random.random() - 1, random.random() - 0.5)
        self.vel.scale_to_length(self.speed)

class Game:
    def __init__(self, fps=60, init_speed=600, max_speed=3000, max_score=5, friction=1, restitution=15):
        pygame.init()
        pygame.display.set_caption("Pong")
        self.fps = fps
        self.init_speed = init_speed
        self.max_speed = max_speed
        self.max_score = max_score
        self.friction = friction
        self.restitution = restitution
        self.running = True
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.players = (Player(WIDTH * 0.1, HEIGHT * 0.5, WIDTH * 0.04, HEIGHT * 0.25, init_speed, pygame.K_w, pygame.K_s),
                        Player(WIDTH * 0.9, HEIGHT * 0.5, WIDTH * 0.04, HEIGHT * 0.25, init_speed, pygame.K_PAGEUP, pygame.K_PAGEDOWN))
        self.ball = Ball(WIDTH/2, HEIGHT/2, WIDTH * 0.02, init_speed, max_speed)

    def check_collisions(self):
        for player in self.players:
            cx = max(player.rect.left, min(self.ball.pos.x, player.rect.right))
            cy = max(player.rect.top, min(self.ball.pos.y, player.rect.bottom))
            
            dx = self.ball.pos.x - cx
            dy = self.ball.pos.y - cy
            
            if (dx**2 + dy**2) < self.ball.radius**2:
                if abs(dx) > abs(dy):
                    v = self.ball.vel.magnitude()
                    self.ball.vel.x *= -1
                    self.ball.vel.y += player.velocity * self.friction
                    self.ball.vel.scale_to_length(min(self.ball.max_speed, v + abs(player.velocity) * self.restitution / player.max_speed))
                    self.ball.pos.x = cx + (self.ball.radius if dx > 0 else -self.ball.radius)
                else:
                    self.ball.vel.y *= -1
                    self.ball.pos.y = cy + (self.ball.radius if dy > 0 else -self.ball.radius)
                break

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # bats
        for player in self.players:
            if keys[player.up]:
                player.move(dt, -1)
            if keys[player.down]:
                player.move(dt, 1)
            if not keys[player.up] and not keys[player.down]:
                player.velocity = 0

        # ball
        status = self.ball.move(dt)
        if status != -1:
            self.ball.reset()
            self.players[0].reset()
            self.players[1].reset()
            self.players[status].score += 1
            if self.players[status].score == self.max_score:
                print(f"Player {status + 1} wins!")
                return status
        
        self.check_collisions()
        return -1
    
    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) * 0.001

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.update(dt) != -1:
                self.running = False

            self.draw()
        pygame.quit()

    def draw(self):
        self.screen.fill("white")
        pygame.draw.rect(self.screen, "black", self.players[0].rect)
        pygame.draw.rect(self.screen, "black", self.players[1].rect)
        pygame.draw.circle(self.screen, "black", self.ball.pos, self.ball.radius)
        if pygame.font:
            font = pygame.font.Font(None, 64)
            text = font.render(f"{self.players[0].score} - {self.players[1].score}", True, "black")
            pos = text.get_rect(centerx=self.screen.get_width()/2, y=10)
            self.screen.blit(text, pos)
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()