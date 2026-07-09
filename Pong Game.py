import math
import random
import tkinter as tk

WIDTH = 1000
HEIGHT = 600
BG = "#0f121c"
WHITE = "#f0f0f5"
ACCENT = "#5ac8ff"
SCORE_COLOR = "#ffdc78"
LINE_COLOR = "#3c465f"

PADDLE_W = 16
PADDLE_H = 110
PADDLE_MARGIN = 40
PADDLE_BASE_SPEED = 8.0
PADDLE_MAX_SPEED = 26.0
PADDLE_SENSITIVITY = 0.03

BALL_SIZE = 18
BASE_BALL_SPEED = 6.0
MAX_BALL_SPEED = 24.0
BALL_SPEED_MULTIPLIER = 1.07
MAX_BOUNCE_ANGLE = math.radians(60)
FRAME_MS = 16


def clamp(value, low, high):
    return max(low, min(high, value))


class PongGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Speed Pong")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.keys_pressed = set()
        self.left_score = 0
        self.right_score = 0

        self.left_paddle = {
            "x": PADDLE_MARGIN,
            "y": HEIGHT / 2 - PADDLE_H / 2,
            "w": PADDLE_W,
            "h": PADDLE_H,
        }
        self.right_paddle = {
            "x": WIDTH - PADDLE_MARGIN - PADDLE_W,
            "y": HEIGHT / 2 - PADDLE_H / 2,
            "w": PADDLE_W,
            "h": PADDLE_H,
        }
        self.ball = {
            "x": WIDTH / 2 - BALL_SIZE / 2,
            "y": HEIGHT / 2 - BALL_SIZE / 2,
            "size": BALL_SIZE,
        }

        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.reset_ball(random.choice([-1, 1]))

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        self.draw_static_elements()
        self.game_loop()

    def on_key_press(self, event):
        self.keys_pressed.add(event.keysym.lower())

    def on_key_release(self, event):
        self.keys_pressed.discard(event.keysym.lower())

    def reset_ball(self, direction):
        self.ball["x"] = WIDTH / 2 - BALL_SIZE / 2
        self.ball["y"] = HEIGHT / 2 - BALL_SIZE / 2
        angle = random.uniform(-0.6, 0.6)
        self.ball_vx = math.cos(angle) * BASE_BALL_SPEED * direction
        self.ball_vy = math.sin(angle) * BASE_BALL_SPEED

    def current_ball_speed(self):
        return math.hypot(self.ball_vx, self.ball_vy)

    def dynamic_paddle_speed(self):
        return min(
            PADDLE_MAX_SPEED,
            PADDLE_BASE_SPEED + max(0.0, self.current_ball_speed() - BASE_BALL_SPEED) * PADDLE_SENSITIVITY * 60,
        )

    def move_paddles(self):
        paddle_speed = self.dynamic_paddle_speed()

        if "w" in self.keys_pressed:
            self.left_paddle["y"] -= paddle_speed
        if "s" in self.keys_pressed:
            self.left_paddle["y"] += paddle_speed
        if "up" in self.keys_pressed:
            self.right_paddle["y"] -= paddle_speed
        if "down" in self.keys_pressed:
            self.right_paddle["y"] += paddle_speed

        self.left_paddle["y"] = clamp(self.left_paddle["y"], 0, HEIGHT - PADDLE_H)
        self.right_paddle["y"] = clamp(self.right_paddle["y"], 0, HEIGHT - PADDLE_H)

    def rects_intersect(self, a, b):
        return not (
            a["x"] + a["w"] < b["x"] or
            a["x"] > b["x"] + b["w"] or
            a["y"] + a["h"] < b["y"] or
            a["y"] > b["y"] + b["h"]
        )

    def update_ball(self):
        self.ball["x"] += self.ball_vx
        self.ball["y"] += self.ball_vy

        if self.ball["y"] <= 0:
            self.ball["y"] = 0
            self.ball_vy *= -1
        elif self.ball["y"] + BALL_SIZE >= HEIGHT:
            self.ball["y"] = HEIGHT - BALL_SIZE
            self.ball_vy *= -1

        if self.ball["x"] + BALL_SIZE < 0:
            self.right_score += 1
            self.reset_ball(-1)
            return
        elif self.ball["x"] > WIDTH:
            self.left_score += 1
            self.reset_ball(1)
            return

        ball_rect = {"x": self.ball["x"], "y": self.ball["y"], "w": BALL_SIZE, "h": BALL_SIZE}

        if self.ball_vx < 0 and self.rects_intersect(ball_rect, self.left_paddle):
            self.ball["x"] = self.left_paddle["x"] + self.left_paddle["w"]
            self.apply_paddle_bounce(self.left_paddle, moving_right=True)
        elif self.ball_vx > 0 and self.rects_intersect(ball_rect, self.right_paddle):
            self.ball["x"] = self.right_paddle["x"] - BALL_SIZE
            self.apply_paddle_bounce(self.right_paddle, moving_right=False)

    def apply_paddle_bounce(self, paddle, moving_right):
        paddle_center = paddle["y"] + paddle["h"] / 2
        ball_center = self.ball["y"] + BALL_SIZE / 2
        relative_intersect = (ball_center - paddle_center) / (paddle["h"] / 2)
        relative_intersect = clamp(relative_intersect, -1.0, 1.0)
        bounce_angle = relative_intersect * MAX_BOUNCE_ANGLE

        new_speed = min(MAX_BALL_SPEED, self.current_ball_speed() * BALL_SPEED_MULTIPLIER)
        horizontal = math.cos(bounce_angle) * new_speed
        vertical = math.sin(bounce_angle) * new_speed

        self.ball_vx = abs(horizontal) if moving_right else -abs(horizontal)
        self.ball_vy = vertical

    def draw_static_elements(self):
        self.canvas.delete("all")
        for y in range(0, HEIGHT, 34):
            self.canvas.create_rectangle(WIDTH / 2 - 3, y, WIDTH / 2 + 3, y + 20, fill=LINE_COLOR, outline=LINE_COLOR)

    def draw(self):
        self.draw_static_elements()

        self.canvas.create_rectangle(
            self.left_paddle["x"],
            self.left_paddle["y"],
            self.left_paddle["x"] + self.left_paddle["w"],
            self.left_paddle["y"] + self.left_paddle["h"],
            fill=ACCENT,
            outline=ACCENT,
        )
        self.canvas.create_rectangle(
            self.right_paddle["x"],
            self.right_paddle["y"],
            self.right_paddle["x"] + self.right_paddle["w"],
            self.right_paddle["y"] + self.right_paddle["h"],
            fill=ACCENT,
            outline=ACCENT,
        )
        self.canvas.create_oval(
            self.ball["x"],
            self.ball["y"],
            self.ball["x"] + BALL_SIZE,
            self.ball["y"] + BALL_SIZE,
            fill=WHITE,
            outline=WHITE,
        )

        self.canvas.create_text(WIDTH / 2 - 90, 60, text=str(self.left_score), fill=SCORE_COLOR, font=("Consolas", 48, "bold"))
        self.canvas.create_text(WIDTH / 2 + 90, 60, text=str(self.right_score), fill=SCORE_COLOR, font=("Consolas", 48, "bold"))

        hud = f"Ball Speed: {int(self.current_ball_speed() * 100)}   Paddle Speed: {int(self.dynamic_paddle_speed() * 100)}"
        self.canvas.create_text(WIDTH / 2, HEIGHT - 28, text=hud, fill=WHITE, font=("Consolas", 16, "bold"))
        self.canvas.create_text(
            WIDTH / 2,
            20,
            text="W/S = Left Paddle    Up/Down = Right Paddle",
            fill="#c8d0dd",
            font=("Consolas", 16),
        )

    def game_loop(self):
        self.move_paddles()
        self.update_ball()
        self.draw()
        self.root.after(FRAME_MS, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    PongGame(root)
    root.mainloop()
