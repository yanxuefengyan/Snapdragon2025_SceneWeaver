#!/usr/bin/env python3
"""
最简单的引擎测试 - 验证窗口显示
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("SceneWeaver 窗口显示测试")
print("=" * 60)

try:
    # 1. 导入 pygame
    print("\n1. 导入 pygame...")
    import pygame
    print("   ✓ Pygame 导入成功")
    
    # 2. 初始化
    print("\n2. 初始化 pygame...")
    pygame.init()
    print("   ✓ Pygame 初始化完成")
    
    # 3. 创建窗口
    print("\n3. 创建窗口...")
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
    pygame.display.set_caption("SceneWeaver 测试")
    print(f"   ✓ 窗口创建成功：{width}x{height}")
    
    # 4. 创建时钟
    clock = pygame.time.Clock()
    
    # 5. 主循环
    print("\n4. 进入主循环...")
    print("   提示：窗口应该已经显示")
    print("   按 ESC 键退出")
    print("=" * 60)
    
    running = True
    angle = 0
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清屏
        screen.fill((30, 30, 50))
        
        # 绘制旋转的正方形
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
        
        # 更新显示
        pygame.display.flip()
        clock.tick(60)
        
        angle += 1
    
    print("\n✅ 测试成功！")
    pygame.quit()
    
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()
