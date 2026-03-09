"""
SceneWeaver 单元测试运行器
直接运行各个测试模块
"""

import unittest
import sys
from pathlib import Path
import time
from datetime import datetime

def run_individual_tests():
    """逐个运行测试文件"""
    print("=" * 60)
    print("🎮 SceneWeaver 单元测试执行")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试文件列表
    test_files = [
        'tests.test_core_engine',
        'tests.test_lighting', 
        'tests.test_resource_manager',
        'tests.test_particle_system',
        'tests.test_ai_system',
        'tests.test_object_detection',
        'tests.test_gui_system',
        'tests.test_input_handler'
    ]
    
    # 存储测试结果
    results = []
    total_start_time = time.time()
    
    for test_file in test_files:
        print(f"🧪 运行测试: {test_file}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # 动态导入并运行测试
            module = __import__(test_file, fromlist=[''])
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            # 运行测试
            runner = unittest.TextTestRunner(verbosity=1)
            result = runner.run(suite)
            
            end_time = time.time()
            
            # 记录结果
            test_result = {
                'module': test_file,
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'time': end_time - start_time,
                'success': result.wasSuccessful()
            }
            results.append(test_result)
            
            # 显示结果
            status = "✅ 通过" if result.wasSuccessful() else "❌ 失败"
            print(f"结果: {status} (运行{result.testsRun}个测试, {end_time-start_time:.2f}秒)")
            
            if result.failures:
                print(f"失败: {len(result.failures)} 个")
            if result.errors:
                print(f"错误: {len(result.errors)} 个")
                
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            results.append({
                'module': test_file,
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'time': 0,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # 显示汇总报告
    total_end_time = time.time()
    generate_summary_report(results, total_end_time - total_start_time)
    
    return all(r['success'] for r in results if 'success' in r)

def generate_summary_report(results, total_time):
    """生成测试汇总报告"""
    print("=" * 60)
    print("📋 测试汇总报告")
    print("=" * 60)
    
    total_tests = sum(r['tests_run'] for r in results)
    total_failures = sum(r['failures'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    successful_modules = sum(1 for r in results if r.get('success', False))
    
    print(f"测试模块总数: {len(results)}")
    print(f"成功模块: {successful_modules}")
    print(f"失败模块: {len(results) - successful_modules}")
    print(f"总测试数: {total_tests}")
    print(f"总失败数: {total_failures}")
    print(f"总错误数: {total_errors}")
    print(f"总耗时: {total_time:.2f} 秒")
    
    if total_tests > 0:
        success_rate = ((total_tests - total_failures - total_errors) / total_tests) * 100
        print(f"成功率: {success_rate:.1f}%")
    
    print("\n📊 详细结果:")
    print("-" * 40)
    
    for result in results:
        status = "✅" if result.get('success', False) else "❌"
        time_str = f"{result['time']:.2f}s" if result['time'] > 0 else "N/A"
        print(f"{status} {result['module']:<30} {result['tests_run']:>3} tests, {time_str}")
        
        if not result.get('success', True):
            if 'error' in result:
                print(f"    错误: {result['error']}")
            elif result['failures'] > 0:
                print(f"    失败: {result['failures']} 个测试")
            elif result['errors'] > 0:
                print(f"    错误: {result['errors']} 个测试")

def main():
    """主函数"""
    try:
        all_passed = run_individual_tests()
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 所有测试通过！")
            print("✅ SceneWeaver核心功能稳定可靠")
        else:
            print("⚠️  部分测试未通过")
            print("🔧 请检查上述失败的测试模块")
        print("=" * 60)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n💥 测试执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)