"""
Stage 4 Demo - 第四阶段功能演示
演示SceneWeaver第四阶段的插件系统、社区功能和商业化特性
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from plugins.plugin_manager import PluginManager
from plugins.plugin_market import PluginMarket, PluginMarketFactory
from plugins.sdk import PluginDevelopmentHelper
from community.work_sharing import WorkSharingPlatform, LocalWorkSharing
from community.tutorials import TutorialSystem, LocalTutorialSystem
from commerce.licensing import CommerceSystem, CommerceSystemFactory


def demo_plugin_system():
    """演示插件系统功能"""
    print("=== 插件系统演示 ===")
    
    # 创建插件管理器
    plugin_manager = PluginManager("plugins")
    
    # 发现插件
    print("1. 发现可用插件...")
    available_plugins = plugin_manager.discover_plugins()
    print(f"   发现 {len(available_plugins)} 个插件:")
    for plugin in available_plugins:
        print(f"   - {plugin.name} ({plugin.version}) - {plugin.description}")
    
    # 加载插件
    print("\n2. 加载插件...")
    for plugin in available_plugins:
        if plugin_manager.load_plugin(plugin.name):
            print(f"   ✓ 插件加载成功: {plugin.name}")
        else:
            print(f"   ✗ 插件加载失败: {plugin.name}")
    
    # 激活插件
    print("\n3. 激活插件...")
    for plugin_name in plugin_manager.list_plugins():
        if plugin_manager.activate_plugin(plugin_name):
            print(f"   ✓ 插件激活成功: {plugin_name}")
        else:
            print(f"   ✗ 插件激活失败: {plugin_name}")
    
    # 显示激活的插件
    active_plugins = plugin_manager.get_active_plugins()
    print(f"\n4. 当前激活的插件: {len(active_plugins)} 个")
    for plugin_name in active_plugins:
        plugin_info = plugin_manager.get_plugin_info(plugin_name)
        if plugin_info:
            print(f"   - {plugin_info.name} ({plugin_info.plugin_type.value})")
    
    return plugin_manager


def demo_plugin_market():
    """演示插件市场功能"""
    print("\n=== 插件市场演示 ===")
    
    # 创建本地插件市场（用于演示）
    market = PluginMarketFactory.create_market_client("local", local_path="local_plugins")
    
    # 搜索插件
    print("1. 搜索插件...")
    plugins = market.search_plugins(query="render", sort_by="rating")
    print(f"   找到 {len(plugins)} 个相关插件")
    
    # 显示推荐插件
    print("\n2. 推荐插件...")
    featured = market.get_featured_plugins(limit=3)
    for plugin in featured:
        print(f"   - {plugin.name} (v{plugin.version}) - {plugin.description}")
        print(f"     评分: {plugin.rating}/5.0 | 下载: {plugin.download_count}")
    
    # 显示分类
    print("\n3. 插件分类...")
    categories = market.get_plugin_categories()
    for category in categories:
        category_plugins = market.get_plugins_by_category(category)
        print(f"   {category}: {len(category_plugins)} 个插件")


def demo_plugin_development():
    """演示插件开发功能"""
    print("\n=== 插件开发演示 ===")
    
    # 创建插件脚手架
    print("1. 创建插件脚手架...")
    plugin_dir = PluginDevelopmentHelper.create_plugin_scaffold(
        plugin_name="my_custom_effect",
        plugin_type="render_effect",
        output_dir="plugins",
        version="1.0.0",
        author="Demo Developer",
        description="我的自定义渲染效果插件"
    )
    
    if plugin_dir:
        print(f"   ✓ 插件脚手架创建成功: {plugin_dir}")
        
        # 验证插件代码
        print("\n2. 验证插件代码...")
        errors = PluginDevelopmentHelper.validate_plugin_code(plugin_dir)
        if errors:
            print("   发现代码问题:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("   ✓ 代码验证通过")
    else:
        print("   ✗ 插件脚手架创建失败")


def demo_community_features():
    """演示社区功能"""
    print("\n=== 社区功能演示 ===")
    
    # 创建本地作品分享平台
    sharing = LocalWorkSharing("local_works")
    
    # 用户认证
    print("1. 用户认证...")
    if sharing.authenticate("demo_user", "demo_password"):
        print("   ✓ 用户认证成功")
    else:
        print("   ✗ 用户认证失败")
    
    # 搜索作品
    print("\n2. 搜索作品...")
    works = sharing.search_works(query="特效", sort_by="created_time")
    print(f"   找到 {len(works)} 个作品")
    
    for work in works[:3]:  # 显示前3个
        print(f"   - {work.title} by {work.author}")
        print(f"     {work.description[:50]}...")
    
    # 获取热门作品
    print("\n3. 热门作品...")
    popular_works = sharing.get_popular_works(limit=3)
    for work in popular_works:
        print(f"   - {work.title} (👍 {work.like_count})")


def demo_tutorial_system():
    """演示教程系统"""
    print("\n=== 教程系统演示 ===")
    
    # 创建本地教程系统
    tutorial_sys = LocalTutorialSystem("local_tutorials")
    
    # 获取教程列表
    print("1. 获取教程...")
    tutorials = tutorial_sys.get_tutorials(category="basics", difficulty="beginner")
    print(f"   找到 {len(tutorials)} 个基础教程")
    
    for tutorial in tutorials:
        print(f"   - {tutorial.title}")
        print(f"     时长: {tutorial.estimated_time}分钟 | 难度: {tutorial.difficulty}")
    
    # 搜索教程
    print("\n2. 搜索教程...")
    search_results = tutorial_sys.search_tutorials("渲染")
    print(f"   搜索'渲染'找到 {len(search_results)} 个结果")
    
    # 获取推荐教程
    print("\n3. 推荐教程...")
    recommended = tutorial_sys.get_recommended_tutorials(limit=2)
    for tutorial in recommended:
        print(f"   - {tutorial.title} (完成率: {tutorial.completion_rate:.1%})")


def demo_commerce_system():
    """演示商业化系统"""
    print("\n=== 商业化系统演示 ===")
    
    # 创建本地商业系统（用于演示）
    commerce = CommerceSystemFactory.create_commerce_system("local")
    
    # 初始化系统
    print("1. 初始化商业化系统...")
    if commerce.initialize():
        print("   ✓ 系统初始化成功")
    else:
        print("   ✗ 系统初始化失败")
    
    # 显示系统状态
    print("\n2. 系统状态...")
    status = commerce.get_system_status()
    print(f"   许可证状态: {status['license']['status']}")
    print(f"   许可证类型: {status['license'].get('type', 'N/A')}")
    print(f"   订阅状态: {'活跃' if status['subscription']['active'] else '非活跃'}")
    
    # 检查功能权限
    print("\n3. 功能权限检查...")
    features_to_check = ['basic_rendering', 'ai_integration', 'multiplayer']
    for feature in features_to_check:
        enabled = commerce.is_commercial_feature_enabled(feature)
        status_icon = "✓" if enabled else "✗"
        print(f"   {status_icon} {feature}: {'启用' if enabled else '禁用'}")
    
    # 显示定价信息
    print("\n4. 定价信息...")
    pricing = commerce.get_pricing_info()
    for plan_name, plan_info in pricing.items():
        price_str = f"${plan_info['price']}/{plan_info.get('period', '')}" if isinstance(plan_info['price'], (int, float)) else plan_info['price']
        print(f"   {plan_name.capitalize()}: {price_str}")
        print(f"     功能: {', '.join(plan_info['features'][:3])}...")


def main():
    """主演示函数"""
    print("SceneWeaver 第四阶段功能演示")
    print("=" * 50)
    
    try:
        # 演示插件系统
        plugin_manager = demo_plugin_system()
        
        # 演示插件市场
        demo_plugin_market()
        
        # 演示插件开发
        demo_plugin_development()
        
        # 演示社区功能
        demo_community_features()
        
        # 演示教程系统
        demo_tutorial_system()
        
        # 演示商业化系统
        demo_commerce_system()
        
        # 清理资源
        print("\n=== 清理资源 ===")
        if plugin_manager:
            plugin_manager.cleanup()
            print("✓ 插件管理器资源清理完成")
        
        print("\n🎉 第四阶段功能演示完成！")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()