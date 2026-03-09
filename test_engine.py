#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简化的引擎测试 - 直接创建窗口
"""

import sys
import os

# 设置环境变量支持 UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("=" * 60)
    print("Simple Window Test")
    print("=" * 60)
    
    try:
        import pygame
        print("[OK] Pygame imported")
        
        pygame.init()
        print("[OK] Pygame initialized")
        
        # Create window
        width, height = 1280, 720
        screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("SceneWeaver Test Window")
        print(f"[OK] Window created: {width}x{height}")
        
        clock = pygame.time.Clock()
        
        # Main loop
        print("\nEntering main loop...")
        print("Press ESC to exit")
        print("=" * 60)
        
        running = True
        angle = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Clear screen
            screen.fill((30, 30, 50))
            
            # Draw rotating square
            import math
            center_x, center_y = width // 2, height // 2
            size = 150
            
            rad_angle = math.radians(angle)
            cos_a, sin_a = math.cos(rad_angle), math.sin(rad_angle)
            
            points = []
            for x_off, y_off in [(-1,-1), (1,-1), (1,1), (-1,1)]:
                rx = x_off * cos_a - y_off * sin_a
                ry = x_off * sin_a + y_off * cos_a
                points.append((center_x + int(rx * size), center_y + int(ry * size)))
            
            pygame.draw.polygon(screen, (100, 150, 255), points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 3)
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
            
            angle += 1
        
        print("\n[OK] Test completed!")
        pygame.quit()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
