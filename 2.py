
import pygame
import random
import time
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="snake_game",
    user="postgres",
    password="yourpassword" 
)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) PRIMARY KEY
);
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS user_score (
    username VARCHAR(50),
    score INTEGER,
    level INTEGER,
    saved_time TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username)
);
''')
conn.commit()

# Ввод имени пользователя
username = input("Enter your username: ").strip()
cur.execute("SELECT * FROM users WHERE username = %s", (username,))
user = cur.fetchone()
if not user:
    cur.execute("INSERT INTO users (username) VALUES (%s)", (username,))
    conn.commit()
    level = 1
else:
    cur.execute("SELECT level FROM user_score WHERE username = %s ORDER BY saved_time DESC LIMIT 1", (username,))
    level_row = cur.fetchone()
    level = level_row[0] if level_row else 1

# Настройка уровней
LEVELS = {
    1: {"speed": 7, "walls": False},
    2: {"speed": 10, "walls": True},
    3: {"speed": 13, "walls": True},
}

# Настройки Pygame
pygame.init()
WIDTH, HEIGHT = 400, 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Класс Змейки
class Snake:
    def __init__(self):
        self.body = [(100, 100), (80, 100), (60, 100)]
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.grow = False

    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        if self.direction == "UP":
            head_y -= CELL_SIZE
        elif self.direction == "DOWN":
            head_y += CELL_SIZE
        elif self.direction == "LEFT":
            head_x -= CELL_SIZE
        elif self.direction == "RIGHT":
            head_x += CELL_SIZE

        new_head = (head_x, head_y)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        self.body.insert(0, new_head)

    def check_collision(self):
        head_x, head_y = self.body[0]
        if LEVELS[level]["walls"] and (head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT):
            return True
        if (head_x, head_y) in self.body[1:]:
            return True
        return False

    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))

# Класс Еды
class Food:
    def __init__(self, snake_body):
        self.position = self.generate_food(snake_body)
        self.weight = random.randint(1, 3)
        self.spawn_time = time.time()
        self.color = self.get_color()

    def get_color(self):
        return [RED, ORANGE, YELLOW][self.weight - 1]

    def generate_food(self, snake_body):
        while True:
            x = random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE
            y = random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
            if (x, y) not in snake_body:
                return (x, y)

    def draw(self):
        pygame.draw.rect(screen, self.color, (*self.position, CELL_SIZE, CELL_SIZE))

# Основной цикл игры
running = True
paused = False
clock = pygame.time.Clock()
snake = Snake()
food = Food(snake.body)
score = 0
font = pygame.font.Font(None, 30)

while running:
    if not paused:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != "DOWN":
                    snake.next_direction = "UP"
                if event.key == pygame.K_DOWN and snake.direction != "UP":
                    snake.next_direction = "DOWN"
                if event.key == pygame.K_LEFT and snake.direction != "RIGHT":
                    snake.next_direction = "LEFT"
                if event.key == pygame.K_RIGHT and snake.direction != "LEFT":
                    snake.next_direction = "RIGHT"
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    cur.execute('''
                        INSERT INTO user_score (username, score, level, saved_time)
                        VALUES (%s, %s, %s, NOW())
                    ''', (username, score, level))
                    conn.commit()

        snake.move()

        if snake.check_collision():
            running = False

        if snake.body[0] == food.position:
            snake.grow = True
            score += food.weight
            food = Food(snake.body)

        if time.time() - food.spawn_time > 5:
            food = Food(snake.body)

        snake.draw()
        food.draw()
        score_text = font.render(f"Score: {score}", True, BLUE)
        level_text = font.render(f"Level: {level}", True, BLUE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))

        pygame.display.update()
        clock.tick(LEVELS[level]["speed"])

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False

pygame.quit()
cur.close()
conn.close()