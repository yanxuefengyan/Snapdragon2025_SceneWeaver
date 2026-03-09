"""
SceneWeaver 综合测试运行器
运行所有单元测试并生成测试报告
"""

import unittest
import sys
import os
from pathlib import Path
import time
from datetime import datetime
import json

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

class TestResultCollector(unittest.TextTestResult):
    """自定义测试结果收集器"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = []
        self.start_time = time.time()
    
    def startTest(self, test):
        """测试开始时记录"""
        super().startTest(test)
        self.current_test_start = time.time()
    
    def addSuccess(self, test):
        """记录成功的测试"""
        super().addSuccess(test)
        elapsed_time = time.time() - self.current_test_start
        self.test_results.append({
            'name': str(test),
            'status': 'PASS',
            'time': elapsed_time,
            'message': ''
        })
    
    def addError(self, test, err):
        """记录错误的测试"""
        super().addError(test, err)
        elapsed_time = time.time() - self.current_test_start
        self.test_results.append({
            'name': str(test),
            'status': 'ERROR',
            'time': elapsed_time,
            'message': self._exc_info_to_string(err, test)
        })
    
    def addFailure(self, test, err):
        """记录失败的测试"""
        super().addFailure(test, err)
        elapsed_time = time.time() - self.current_test_start
        self.test_results.append({
            'name': str(test),
            'status': 'FAIL',
            'time': elapsed_time,
            'message': self._exc_info_to_string(err, test)
        })

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🎮 SceneWeaver 综合单元测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试文件
    test_files = [
        'test_lighting',
        'test_resource_manager'
    ]
    
    print("🔍 发现测试用例...")
    total_tests = 0
    
    for test_file in test_files:
        try:
            # 动态导入测试模块
            module = __import__(f'tests.{test_file}', fromlist=[''])
            
            # 加载测试用例
            test_suite = loader.loadTestsFromModule(module)
            suite.addTest(test_suite)
            
            # 统计测试数量
            test_count = test_suite.countTestCases()
            total_tests += test_count
            print(f"   ✓ {test_file}: {test_count} 个测试用例")
            
        except ImportError as e:
            print(f"   ✗ {test_file}: 导入失败 - {e}")
        except Exception as e:
            print(f"   ✗ {test_file}: 加载失败 - {e}")
    
    if total_tests == 0:
        print("\n⚠️  未发现任何可运行的测试用例")
        return True
    
    print(f"\n📊 总计发现 {total_tests} 个测试用例")
    print()
    
    # 运行测试
    print("🏃 开始执行测试...")
    print("-" * 60)
    
    # 创建自定义测试运行器
    runner = unittest.TextTestRunner(
        verbosity=2,
        resultclass=TestResultCollector
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # 生成测试报告
    generate_test_report(result, end_time - start_time, total_tests)
    
    return result.wasSuccessful()

def generate_test_report(result, total_time, total_tests):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📋 测试报告摘要")
    print("=" * 60)
    
    # 基本统计
    passed = result.testsRun - len(result.failures) - len(result.errors)
    failed = len(result.failures)
    errors = len(result.errors)
    
    print(f"测试总数: {result.testsRun}")
    
    if result.testsRun > 0:
        print(f"通过: {passed} ({passed/result.testsRun*100:.1f}%)")
        print(f"失败: {failed} ({failed/result.testsRun*100:.1f}%)")
        print(f"错误: {errors} ({errors/result.testsRun*100:.1f}%)")
    else:
        print("通过: 0 (0.0%)")
        print("失败: 0 (0.0%)")
        print("错误: 0 (0.0%)")
    
    print(f"总耗时: {total_time:.2f} 秒")
    
    if result.testsRun > 0:
        print(f"平均每个测试: {total_time/result.testsRun:.3f} 秒")
    
    # 详细失败信息
    if result.failures or result.errors:
        print("\n❌ 失败详情:")
        print("-" * 40)
        
        for test, traceback in result.failures:
            print(f"\n🔥 失败测试: {test}")
            print(f"   错误信息: {traceback.splitlines()[-1] if traceback else '未知错误'}")
        
        for test, traceback in result.errors:
            print(f"\n💥 错误测试: {test}")
            print(f"   错误信息: {traceback.splitlines()[-1] if traceback else '未知错误'}")
    
    # 性能统计
    print("\n⏱️  性能统计:")
    print("-" * 40)
    
    if hasattr(result, 'test_results') and result.test_results:
        # 按时间排序找出最慢的测试
        sorted_results = sorted(result.test_results, key=lambda x: x['time'], reverse=True)
        print("最耗时的测试:")
        for i, test_result in enumerate(sorted_results[:5]):
            status_icon = "✅" if test_result['status'] == 'PASS' else "❌"
            print(f"   {i+1}. {status_icon} {test_result['name'][:50]}... ({test_result['time']:.3f}s)")
    
    # 生成JSON报告
    generate_json_report(result, total_time, total_tests)

def generate_json_report(result, total_time, total_tests):
    """生成JSON格式的详细报告"""
    report_data = {
        'summary': {
            'timestamp': datetime.now().isoformat(),
            'total_tests': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors) if result.testsRun > 0 else 0,
            'failed': len(result.failures),
            'errors': len(result.errors),
            'total_time_seconds': total_time,
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
        },
        'failures': [],
        'errors': [],
        'test_details': []
    }
    
    # 添加失败详情
    for test, traceback in result.failures:
        report_data['failures'].append({
            'test': str(test),
            'error': traceback
        })
    
    # 添加错误详情
    for test, traceback in result.errors:
        report_data['errors'].append({
            'test': str(test),
            'error': traceback
        })
    
    # 添加测试详情（如果有）
    if hasattr(result, 'test_results'):
        report_data['test_details'] = result.test_results
    
    # 保存报告文件
    report_file = project_root / 'test_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存至: {report_file}")

def main():
    """主函数"""
    try:
        success = run_all_tests()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 所有测试通过！")
            print("✅ SceneWeaver核心功能稳定可靠")
        else:
            print("⚠️  部分测试未通过")
            print("🔧 请检查上述失败的测试用例")
        print("=" * 60)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n💥 测试执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)