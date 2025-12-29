import pygame
import asyncio
import platform
import random
import math
import sys
import os

# Hàm xử lý đường dẫn tài nguyên
def resource_path(relative_path):
    """Trả về đường dẫn thật tới file khi chạy exe"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Khởi tạo Pygame và Mixer
pygame.init()
pygame.mixer.init()

#Thiết lập kích thước ảnh
ImageSizeX = 100
ImageSizeY = 100
# Thiết lập cửa sổ
WIDTH = 960
HEIGHT = 540
icon = pygame.image.load(resource_path("assets/icon.png")) 
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chúc Mừng Sinh Nhật")
FPS = 60
clock = pygame.time.Clock()

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PASTEL_PINK = (255, 182, 193)
PASTEL_PURPLE = (200, 162, 200)
PASTEL_YELLOW = (255, 255, 204)
PASTEL_GREEN = (144, 238, 144)

# Emoji bay lên
class EmojiParticle:
    def __init__(self):
        self.emoji = random.choice(["🎉", "🎈", "🎂", "🥳"])
        self.font = pygame.font.SysFont("Segoe UI Emoji", 36)
        self.image = self.font.render(self.emoji, True, WHITE)
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + 20
        self.vy = random.uniform(-1.5, -0.5)
        self.alpha = 255
        self.fade_start_y = HEIGHT * 0.15  # bắt đầu mờ dần khi gần lên đỉnh
        self.dead = False

    def update(self):
        self.y += self.vy
        if self.y < self.fade_start_y:
            self.alpha = max(0, self.alpha - 4)
        if self.alpha <= 0:
            self.dead = True

    def draw(self):
        img = self.image.copy()
        img.set_alpha(self.alpha)
        screen.blit(img, (self.x, self.y))

emoji_particles = []

# Tải tài nguyên (hình ảnh và âm thanh)
dog_frames = []
try:
    for i in range(7):
        frame = pygame.image.load(resource_path(f"assets/frame_{i}_delay-0.05s.gif"))
        frame = pygame.transform.scale(frame, (75, 75))
        dog_frames.append(frame)
except pygame.error:
    for i in range(7):
        frame = pygame.Surface((50, 50))
        frame.fill((100 + i * 20, 50, 50))
        dog_frames.append(frame)
dog_rect = dog_frames[0].get_rect(topleft=(WIDTH - 50, HEIGHT - 100))
dog_speed = -5
dog_frame_index = 0
frame_delay = 0.05
frame_timer = 0
message_flash_timer = 0
message_flash_duration = 0.1

# Hộp quà đóng
try:
    gift_closed = pygame.image.load(resource_path("assets/gift_closed.png"))
    gift_closed = pygame.transform.scale(gift_closed, (50, 50))
except pygame.error:
    gift_closed = pygame.Surface((50, 50))
    gift_closed.fill((200, 100, 100))
gift_closed_original = gift_closed.copy()
gift_rect = gift_closed.get_rect(topleft=(50, HEIGHT - 100))

# Hộp quà mở
try:
    gift_open = pygame.image.load(resource_path("assets/gift_open.png"))
    gift_open = pygame.transform.scale(gift_open, (50, 50))
except pygame.error:
    gift_open = pygame.Surface((50, 50))
    gift_open.fill((100, 200, 100))
gift_open_rect = gift_open.get_rect(topleft=(50, HEIGHT - 100))

# Hiệu ứng pháo hoa
fireworks = []
class Firework:
    def __init__(self, x):
        self.x = x
        self.y = HEIGHT
        self.vy = random.uniform(-5, -3)
        self.explosion_height = random.randint(50, HEIGHT - 50)
        self.particles = []
        self.exploded = False
        self.color = random.choice([PASTEL_PINK, PASTEL_PURPLE, PASTEL_YELLOW, PASTEL_GREEN])

    def update(self):
        self.y += self.vy
        if self.y <= self.explosion_height and not self.exploded:
            self.exploded = True
            for _ in range(30):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 4)
                self.particles.append([0, 0, math.cos(angle) * speed, math.sin(angle) * speed, 30])
        elif self.exploded:
            for p in self.particles[:]:
                p[0] += p[2]
                p[1] += p[3]
                p[4] -= 1
                p[2] *= 0.97
                p[3] *= 0.97
                if p[4] <= 0:
                    self.particles.remove(p)

    def draw(self):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)
        for p in self.particles:
            x, y, _, _, life = p
            size = max(2, life * 0.1)
            pygame.draw.circle(screen, self.color, (int(self.x + x), int(self.y + y)), int(size))

# Hiệu ứng nhân vật bay lên
floating_characters = []
class FloatingCharacter:
    def __init__(self, x):
        self.x = x
        self.y = HEIGHT
        self.vy = random.uniform(-1.2, -0.6)
        self.angle = 0
        self.rotation_speed = random.uniform(1, 3)
        self.alpha = 255
        self.fade_start_y = HEIGHT * 0.15
        character_files = [resource_path(f"assets/bn_{i+1}.png") for i in range(10)]
        try:
            self.image = pygame.image.load(random.choice(character_files))
            self.image = pygame.transform.scale(self.image, (ImageSizeX, ImageSizeX))
            self.original_image = self.image.copy()
        except pygame.error:
            self.image = pygame.Surface((ImageSizeX, ImageSizeX))
            self.image.fill(random.choice([PASTEL_PINK, PASTEL_PURPLE]))
            self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.dead = False

    def update(self):
        self.y += self.vy
        self.angle = (self.angle + self.rotation_speed) % 360
        if self.y < self.fade_start_y:
            self.alpha = max(0, self.alpha - 4)
        if self.alpha <= 0:
            self.dead = True
        self.rect.center = (self.x, self.y)

    def draw(self):
        rad = math.radians(self.angle)
        scale_x = max(0.1, abs(math.cos(rad)))
        scaled = pygame.transform.smoothscale(self.original_image, (int(ImageSizeX * scale_x), ImageSizeY))
        img = scaled.copy()
        img.set_alpha(self.alpha)
        rect = img.get_rect(center=self.rect.center)
        screen.blit(img, rect)

# Hiệu ứng sao
stars = []
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.size = random.uniform(2, 4)
        self.alpha = random.randint(100, 255)
        self.fade_speed = random.uniform(0.5, 1.5)
        self.surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, WHITE, (int(self.size), int(self.size)), int(self.size))
        self.surface.set_alpha(self.alpha)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.fade_speed
        self.surface.set_alpha(self.alpha)
        if self.alpha <= 0:
            self.__init__()

    def draw(self):
        screen.blit(self.surface, (int(self.x - self.size), int(self.y - self.size)))

# Text
try:
    font = pygame.font.Font(resource_path("assets/Lobster-Regular.ttf"), 48)
except:
    font = pygame.font.SysFont("Comic Sans MS", 48)
messages = ["Happy Birthday!", "Chúc m càng ngày càng đẹp", "Luôn vui vẻ", "Làm được nhiều điều mình thích","Quan trọng là!", "Phải kiếm được nhiều tiền", "Để cho t mượn, hẹ hẹ hẹ","Hết =)))" ]
message_index = 0
message_progress = 0
message_timer = 0
message_char_delay = 0.05
display_timer = 0
message_flash_state = True

# Nhạc nền
music_started = False
try:
    pygame.mixer.music.load(resource_path("assets/happy_birthday.mp3"))
except:
    print("Không thể tải file âm thanh")

# Hiệu ứng quà nổ
gift_scaling = False
gift_scale = 1.0
scale_speed = 0.02
max_scale = 1.5
scale_timer = 0
scale_duration = 1.0
show_gift_open = False
gift_open_timer = 0
gift_open_duration = 0.2
explosion_alpha = 0
explosion_fade = False

# Trạng thái trò chơi
dog_moving = True
gift_active = True
celebration_active = False

def draw_typing_text(surface, text, font, color, pos, progress):
    safe_text = text[:progress]
    rendered = font.render(safe_text, True, color)
    outline = font.render(safe_text, True, BLACK)
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            rect = outline.get_rect(center=(pos[0] + dx, pos[1] + dy))
            surface.blit(outline, rect)
    text_rect = rendered.get_rect(center=pos)
    surface.blit(rendered, text_rect)

async def main():
    global dog_frame_index, frame_timer, gift_scale, scale_timer, explosion_alpha, explosion_fade
    global dog_moving, gift_active, gift_scaling, show_gift_open, gift_open_timer, celebration_active
    global message_index, message_timer, message_progress, display_timer, music_started
    global message_flash_timer, message_flash_state
    global floating_characters, fireworks, stars
    global emoji_particles

    def draw_background():
        for y in range(HEIGHT):
            pos = y / HEIGHT
            r = int(182 + (255 - 182) * pos * 0.7)
            g = int(162 + (182 - 162) * (1 - pos))
            b = int(200 + (193 - 200) * (1 - pos))
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not explosion_fade and not celebration_active:
            draw_background()
        else:
            screen.fill(BLACK)

        if dog_moving:
            frame_timer += 1 / FPS
            if frame_timer >= frame_delay:
                dog_frame_index = (dog_frame_index + 1) % len(dog_frames)
                frame_timer = 0
            dog_rect.x += dog_speed
            screen.blit(dog_frames[dog_frame_index], dog_rect)
            if gift_active and dog_rect.colliderect(gift_rect):
                dog_moving = False
                gift_active = False
                gift_scaling = True

        if gift_active:
            screen.blit(gift_closed, gift_rect)
        elif gift_scaling:
            scale_timer += 1 / FPS
            gift_scale += scale_speed
            scaled = pygame.transform.scale(gift_closed_original, (int(50 * gift_scale), int(50 * gift_scale)))
            rect = scaled.get_rect(topleft=(50, HEIGHT - 100))
            screen.blit(scaled, rect)
            if scale_timer >= scale_duration or gift_scale >= max_scale:
                gift_scaling = False
                show_gift_open = True
                scale_timer = 0
        elif show_gift_open:
            screen.blit(gift_open, gift_open_rect)
            gift_open_timer += 1 / FPS
            if gift_open_timer >= gift_open_duration:
                show_gift_open = False
                explosion_alpha = 255
                explosion_fade = True
                gift_open_timer = 0

        if explosion_fade:
            surface = pygame.Surface((WIDTH, HEIGHT))
            surface.fill(WHITE)
            surface.set_alpha(explosion_alpha)
            screen.blit(surface, (0, 0))
            explosion_alpha -= 10
            if explosion_alpha <= 0:
                explosion_fade = False
                celebration_active = True
                for _ in range(1):
                    floating_characters.append(FloatingCharacter(50 + random.randint(-100, 100)))
                for _ in range(10):
                    fireworks.append(Firework(random.randint(0, WIDTH)))
                for _ in range(50):
                    stars.append(Star())
                if not music_started:
                    try:
                        pygame.mixer.music.play(-1)
                        music_started = True
                    except:
                        print("Không thể phát nhạc")

        if celebration_active:
            if random.random() < 0.02:
                floating_characters.append(FloatingCharacter(random.randint(0, WIDTH)))
            if random.random() < 0.12:
                fireworks.append(Firework(random.randint(0, WIDTH)))
            if random.random() < 0.05:
                stars.append(Star())
            if random.random() < 0.03:
                emoji_particles.append(EmojiParticle())

            for emoji in emoji_particles[:]:
                emoji.update()
                emoji.draw()
                if emoji.dead:
                    emoji_particles.remove(emoji)

            for star in stars:
                star.update()
                star.draw()

            for fw in fireworks[:]:
                fw.update()
                fw.draw()
                if not fw.particles and fw.y <= 0:
                    fireworks.remove(fw)

            for char in floating_characters[:]:
                char.update()
                char.draw()
                if char.dead:
                    floating_characters.remove(char)

            if message_index < len(messages):
                message_timer += 1 / FPS
                message_flash_timer += 1 / FPS
                if message_timer >= message_char_delay:
                    message_progress += 1
                    message_timer = 0
                if message_flash_timer >= message_flash_duration:
                    message_flash_state = not message_flash_state
                    message_flash_timer = 0
                draw_typing_text(screen, messages[message_index], font, WHITE, (WIDTH // 2, HEIGHT // 2), message_progress)
                if message_progress >= len(messages[message_index]):
                    display_timer += 1 / FPS
                    if display_timer >= 1:
                        message_index += 1
                        message_progress = 0
                        message_timer = 0
                        display_timer = 0

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())