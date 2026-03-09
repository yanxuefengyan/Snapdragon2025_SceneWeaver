"""
SceneWeaver 正确的测试运行器
确保Python路径设置正确
"""

import sys
import os
from pathlib import Path
import unittest
import time
from datetime import datetime

# 获取项目根目录
project_root = Path(__file__).parent.absolute()
print(f"项目根目录: {project_root}")

# 将项目根目录和src目录添加到Python路径
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("Python路径已更新:")
for i, path in enumerate(sys.path[:5]):  # 只显示前5个路径
    print(f"  {i}: {path}")

def run_test_file(test_filename):
    """运行单个测试文件"""
    print(f"\n🧪 运行测试文件: {test_filename}")
    print("-" * 50)
    
    try:
        # 构造完整的文件路径
        test_file_path = project_root / "tests" / test_filename
        
        if not test_file_path.exists():
            print(f"❌ 测试文件不存在: {test_file_path}")
            return False
        
        # 动态执行测试文件
        start_time = time.time()
        
        # 读取并执行测试文件
        with open(test_file_path, 'r', encoding='utf-8') as f:
            test_code = f.read()
        
        # 创建命名空间
        namespace = {
            '__file__': str(test_file_path),
            '__name__': '__main__',
            'unittest': unittest,
            'sys': sys,
            'Path': Path,
            'np': __import__('numpy') if 'numpy' in sys.modules else None
        }
        
        # 执行测试代码
        exec(test_code, namespace)
        
        end_time = time.time()
        print(f"✅ 测试执行完成 ({end_time - start_time:.2f}秒)")
        return True
        
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎮 SceneWeaver 单元测试执行器")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试文件列表
    test_files = [
        "test_lighting.py",
        "test_resource_manager.py"
    ]
    
    print(f"\n发现 {len(test_files)} 个测试文件")
    
    # 运行测试
    results = []
    for test_file in test_files:
        success = run_test_file(test_file)
        results.append((test_file, success))
    
    # 生成报告
    print("\n" + "=" * 60)
    print("📋 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"总测试文件: {len(results)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed > 0:
        print("\n❌ 失败的测试:")
        for test_file, success in results:
            if not success:
                print(f"  - {test_file}")
    
    print("\n" + "=" * 60)
    if passed == len(results):
        print("🎉 所有测试通过！")
        print("✅ SceneWeaver核心功能稳定可靠")
        return 0
    else:
        print("⚠️  部分测试未通过")
        print("🔧 请检查上述失败的测试")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)