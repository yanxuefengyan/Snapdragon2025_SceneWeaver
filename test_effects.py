#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特效功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pygame
import random
import math

# 初始化
pygame.init()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("特效测试")
clock = pygame.time.Clock()
font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 24)

# 粒子数组
explosion_particles = []
smoke_particles = []
fire_particles = []
magic_particles = []
sparkle_particles = []

def create_explosion():
    center_x, center_y = width // 2, height // 2
    for i in range(100):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5, 15)
        explosion_particles.append({
            "x": center_x,
            "y": center_y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "radius": random.randint(3, 8),
            "color": (random.randint(200, 255), random.randint(50, 150), random.randint(0, 50)),
            "life": 60,
            "max_life": 60
        })

def create_smoke():
    center_x, center_y = width // 2, height // 2
    for i in range(80):
        smoke_particles.append({
            "x": center_x + random.randint(-50, 50),
            "y": center_y + random.randint(-50, 50),
            "vx": random.uniform(-2, 2),
            "vy": random.uniform(-5, -1),
            "radius": random.randint(10, 30),
            "color": (random.randint(150, 200), random.randint(150, 200), random.randint(150, 200)),
            "life": 120,
            "max_life": 120
        })

def create_fire():
    center_x, center_y = width // 2, height // 2 + 50
    for i in range(120):
        fire_particles.append({
            "x": center_x + random.randint(-80, 80),
            "y": center_y,
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-8, -2),
            "radius": random.randint(5, 15),
            "color": (255, random.randint(100, 200), 0),
            "life": 80,
            "max_life": 80
        })

def create_magic():
    center_x, center_y = width // 2, height // 2
    for i in range(60):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(20, 150)
        magic_particles.append({
            "x": center_x + math.cos(angle) * distance,
            "y": center_y + math.sin(angle) * distance,
            "vx": -math.cos(angle) * 2,
            "vy": -math.sin(angle) * 2,
            "radius": random.randint(3, 6),
            "color": (random.randint(150, 255), random.randint(100, 200), 255),
            "life": 100,
            "max_life": 100,
            "rotation": random.uniform(0, 360)
        })

def create_sparkle():
    center_x, center_y = width // 2, height // 2
    for i in range(150):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(8, 20)
        sparkle_particles.append({
            "x": center_x,
            "y": center_y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "radius": random.randint(2, 5),
            "color": (255, 255, random.randint(200, 255)),
            "life": 40,
            "max_life": 40,
            "sparkle": True
        })

def update_and_draw_effects():
    # 爆炸
    for particle in explosion_particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["vx"] *= 0.95
        particle["vy"] *= 0.95
        particle["life"] -= 1
        alpha = int(255 * (particle["life"] / particle["max_life"]))
        color = tuple(min(255, c * alpha // 255) for c in particle["color"])
        pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), particle["radius"])
        if particle["life"] <= 0:
            explosion_particles.remove(particle)
    
    # 烟雾
    for particle in smoke_particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["radius"] += 0.3
        particle["life"] -= 1
        alpha = int(200 * (particle["life"] / particle["max_life"]))
        color = (alpha, alpha, alpha)
        pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), int(particle["radius"]))
        if particle["life"] <= 0:
            smoke_particles.remove(particle)
    
    # 火焰
    for particle in fire_particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["radius"] *= 0.95
        particle["life"] -= 1
        green = int(100 * (particle["life"] / particle["max_life"]))
        color = (255, green, 0)
        pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), int(particle["radius"]))
        if particle["life"] <= 0 or particle["radius"] < 1:
            fire_particles.remove(particle)
    
    # 魔法
    for particle in magic_particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["rotation"] += 5
        particle["life"] -= 1
        alpha = int(255 * (particle["life"] / particle["max_life"]))
        color = tuple(min(255, c * alpha // 255) for c in particle["color"])
        pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), particle["radius"])
        glow_radius = particle["radius"] + int(5 * (particle["life"] / particle["max_life"]))
        pygame.draw.circle(screen, (alpha//3, alpha//3, alpha), (int(particle["x"]), int(particle["y"])), glow_radius, 2)
        if particle["life"] <= 0:
            magic_particles.remove(particle)
    
    # 火花
    for particle in sparkle_particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["vy"] += 0.3
        particle["life"] -= 1
        if particle["life"] % 4 < 2:
            color = particle["color"]
        else:
            color = (255, 255, 255)
        pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), particle["radius"])
        if particle["life"] <= 0:
            sparkle_particles.remove(particle)

# 主循环
running = True
print("=" * 60)
print("特效测试程序")
print("=" * 60)
print("按键 1-5 测试不同特效:")
print("  1 - 爆炸效果")
print("  2 - 烟雾效果")
print("  3 - 火焰效果")
print("  4 - 魔法效果")
print("  5 - 火花效果")
print("ESC - 退出")
print("=" * 60)

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_1:
                create_explosion()
                print("触发：爆炸效果")
            elif event.key == pygame.K_2:
                create_smoke()
                print("触发：烟雾效果")
            elif event.key == pygame.K_3:
                create_fire()
                print("触发：火焰效果")
            elif event.key == pygame.K_4:
                create_magic()
                print("触发：魔法效果")
            elif event.key == pygame.K_5:
                create_sparkle()
                print("触发：火花效果")
    
    screen.fill((30, 30, 50))
    
    # 绘制特效
    update_and_draw_effects()
    
    # 绘制提示
    text = font.render("按 1-5 键触发特效，ESC 退出", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    
    pygame.display.flip()

pygame.quit()
print("\n测试结束！")
