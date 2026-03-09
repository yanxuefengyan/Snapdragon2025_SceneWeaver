#!/usr/bin/env python3
"""
简单的窗口测试程序
"""

import pygame
import time

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("SceneWeaver 测试窗口")

running = True
clock = pygame.time.Clock()
start_time = time.time()

print("窗口已创建，将在 5 秒后自动关闭...")

try:
    while running:
        # 检查时间
        if time.time() - start_time > 5:
            print("测试完成！")
            break
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清屏
        screen.fill((50, 50, 50))  # 深灰色背景
        
        # 绘制一些内容
        pygame.draw.circle(screen, (255, 0, 0), (640, 360), 100)
        font = pygame.font.Font(None, 74)
        text = font.render("SceneWeaver", True, (255, 255, 255))
        screen.blit(text, (640 - text.get_width()//2, 360 - text.get_height()//2))
        
        # 更新显示
        pygame.display.flip()
        clock.tick(60)
        
finally:
    pygame.quit()
    print("窗口已关闭")
