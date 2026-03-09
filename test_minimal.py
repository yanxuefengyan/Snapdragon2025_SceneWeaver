#!/usr/bin/env python3
"""
最简化的渲染测试 - 用于排查窗口显示问题
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("=" * 60)
    print("SceneWeaver 最简化渲染测试")
    print("=" * 60)
    
    try:
        import pygame
        print("✓ Pygame 导入成功")
        
        # 初始化 pygame
        pygame.init()
        print("✓ Pygame 初始化完成")
        
        # 创建窗口
        width, height = 1280, 720
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("SceneWeaver 测试窗口")
        print(f"✓ 窗口创建成功：{width}x{height}")
        
        # 初始化时钟
        clock = pygame.time.Clock()
        
        # 颜色
        WHITE = (255, 255, 255)
        BLUE = (0, 100, 255)
        
        # 旋转角度
        angle = 0
        
        print("\n窗口已打开！")
        print("按 ESC 键退出，或关闭窗口")
        print("=" * 60)
        
        running = True
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # 清屏
            screen.fill((30, 30, 30))
            
            # 绘制一个旋转的正方形
            center_x, center_y = width // 2, height // 2
            size = 100
            
            # 计算旋转后的顶点
            import math
            rad_angle = math.radians(angle)
            cos_a, sin_a = math.cos(rad_angle), math.sin(rad_angle)
            
            points = []
            for x_off, y_off in [(-1,-1), (1,-1), (1,1), (-1,1)]:
                # 旋转
                rx = x_off * cos_a - y_off * sin_a
                ry = x_off * sin_a + y_off * cos_a
                points.append((center_x + int(rx * size), center_y + int(ry * size)))
            
            # 绘制正方形
            pygame.draw.polygon(screen, BLUE, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            
            # 绘制文字
            font = pygame.font.Font(None, 48)
            text = font.render("SceneWeaver", True, WHITE)
            text_rect = text.get_rect(center=(center_x, center_y - 150))
            screen.blit(text, text_rect)
            
            # 更新显示
            pygame.display.flip()
            
            # 控制帧率
            clock.tick(60)
            
            # 更新角度
            angle += 1
        
        print("\n测试结束！")
        pygame.quit()
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败！")
