"""
Resource Manager Tests - 资源管理器测试
验证资源加载、缓存和管理功能
"""

import sys
from pathlib import Path
import tempfile
import shutil

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import logging
from utils.resource_manager import ResourceManager, ResourceType, CacheStrategy


def test_resource_manager_initialization():
    """测试资源管理器初始化"""
    print("🧪 测试资源管理器初始化...")
    try:
        config = {
            'model_path': './test_models',
            'texture_path': './test_textures',
            'cache_path': './test_cache',
            'max_cache_size_mb': 100
        }
        
        rm = ResourceManager(config)
        assert rm is not None, "资源管理器创建失败"
        assert rm.max_cache_size == 100 * 1024 * 1024, "缓存大小设置错误"
        assert rm.cache_strategy == CacheStrategy.LRU, "默认缓存策略错误"
        
        # 测试初始化
        success = rm.initialize()
        assert success, "资源管理器初始化失败"
        
        print("   ✅ 资源管理器初始化测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 资源管理器初始化测试失败: {e}")
        return False


def test_resource_registration():
    """测试资源注册"""
    print("🧪 测试资源注册...")
    try:
        # 创建临时测试文件
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / "test_model.obj"
        test_file.write_text("# Test OBJ file\n")
        
        config = {'cache_path': str(temp_dir / 'cache')}
        rm = ResourceManager(config)
        rm.initialize()
        
        # 注册资源
        success = rm.register_resource(
            resource_id="test_model_001",
            resource_type=ResourceType.MODEL,
            file_path=str(test_file),
            version="1.0.0",
            metadata={"author": "Test"}
        )
        
        assert success, "资源注册失败"
        assert "test_model_001" in rm.resources, "资源未在注册表中找到"
        
        # 验证资源元数据
        metadata = rm.get_resource_info("test_model_001")
        assert metadata is not None, "获取资源信息失败"
        assert metadata.resource_type == ResourceType.MODEL, "资源类型错误"
        assert metadata.version == "1.0.0", "版本信息错误"
        assert metadata.metadata["author"] == "Test", "元数据错误"
        
        print("   ✅ 资源注册测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 资源注册测试失败: {e}")
        return False
    finally:
        # 清理临时目录
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_resource_loading():
    """测试资源加载"""
    print("🧪 测试资源加载...")
    try:
        # 创建临时测试文件
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / "test_texture.txt"  # 改为txt文件避免格式问题
        test_file.write_text("TEXTURE_FILE_CONTENT")
        
        config = {'cache_path': str(temp_dir / 'cache')}
        rm = ResourceManager(config)
        rm.initialize()
        
        # 注册并加载资源
        rm.register_resource(
            resource_id="test_texture_001",
            resource_type=ResourceType.TEXTURE,
            file_path=str(test_file)
        )
        
        # 加载资源（对于非图像文件，应该返回文件路径字符串）
        resource_data = rm.load_resource("test_texture_001")
        assert resource_data is not None, "资源加载失败"
        assert isinstance(resource_data, str), "资源数据类型错误"
        assert "test_texture.txt" in resource_data, "返回的不是文件路径"
        
        # 测试缓存
        cached_data = rm.load_resource("test_texture_001")
        assert cached_data is not None, "缓存资源加载失败"
        assert cached_data == resource_data, "缓存数据不一致"
        
        print("   ✅ 资源加载测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 资源加载测试失败: {e}")
        return False
    finally:
        # 清理临时目录
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_resource_listing():
    """测试资源列表功能"""
    print("🧪 测试资源列表...")
    try:
        temp_dir = Path(tempfile.mkdtemp())
        config = {'cache_path': str(temp_dir / 'cache')}
        rm = ResourceManager(config)
        rm.initialize()
        
        # 创建测试资源
        test_files = []
        for i in range(3):
            test_file = temp_dir / f"test_model_{i}.obj"
            test_file.write_text(f"# Test model {i}\n")
            test_files.append(test_file)
            
            rm.register_resource(
                resource_id=f"test_model_{i:03d}",
                resource_type=ResourceType.MODEL,
                file_path=str(test_file)
            )
        
        # 测试列表功能
        all_resources = rm.list_resources()
        assert len(all_resources) == 3, "资源总数错误"
        
        model_resources = rm.list_resources(ResourceType.MODEL)
        assert len(model_resources) == 3, "模型资源数量错误"
        
        texture_resources = rm.list_resources(ResourceType.TEXTURE)
        assert len(texture_resources) == 0, "纹理资源数量应该为0"
        
        print("   ✅ 资源列表测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 资源列表测试失败: {e}")
        return False
    finally:
        # 清理临时目录
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_cache_management():
    """测试缓存管理"""
    print("🧪 测试缓存管理...")
    try:
        temp_dir = Path(tempfile.mkdtemp())
        config = {
            'cache_path': str(temp_dir / 'cache'),
            'max_cache_size_mb': 1  # 1MB限制
        }
        rm = ResourceManager(config)
        rm.initialize()
        
        # 创建大文件测试缓存限制
        large_file = temp_dir / "large_file.dat"
        large_file.write_bytes(b'x' * (512 * 1024))  # 512KB
        
        # 注册大文件
        rm.register_resource(
            resource_id="large_resource",
            resource_type=ResourceType.MODEL,
            file_path=str(large_file)
        )
        
        # 加载资源
        data = rm.load_resource("large_resource")
        assert data is not None, "大文件资源加载失败"
        assert "large_resource" in rm.resource_cache, "资源未缓存"
        
        print("   ✅ 缓存管理测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 缓存管理测试失败: {e}")
        return False
    finally:
        # 清理临时目录
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """主测试函数"""
    print("=" * 60)
    print("SceneWeaver 资源管理器测试")
    print("=" * 60)
    print()
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        test_resource_manager_initialization,
        test_resource_registration,
        test_resource_loading,
        test_resource_listing,
        test_cache_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"测试结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有资源管理器测试通过！")
        print("\n下一步建议:")
        print("1. 集成到主引擎系统中")
        print("2. 测试实际资源加载性能")
        print("3. 验证网络资源下载功能")
    else:
        print("⚠️  部分测试失败，请检查相关组件。")


if __name__ == "__main__":
    main()