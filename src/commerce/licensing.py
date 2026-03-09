"""
Licensing System - 许可证管理系统
SceneWeaver商业化许可和订阅管理系统
"""

import os
import json
import hashlib
import hmac
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """许可证类型"""
    FREE = "free"           # 免费版
    PERSONAL = "personal"   # 个人版
    PROFESSIONAL = "professional"  # 专业版
    ENTERPRISE = "enterprise"      # 企业版
    TRIAL = "trial"         # 试用版


class SubscriptionStatus(Enum):
    """订阅状态"""
    ACTIVE = "active"
    EXpired = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


@dataclass
class LicenseInfo:
    """许可证信息"""
    license_key: str
    license_type: LicenseType
    user_email: str
    user_name: str
    organization: str = ""
    issue_date: str = ""
    expiry_date: str = ""
    max_devices: int = 1
    features: List[str] = field(default_factory=list)
    signature: str = ""
    is_valid: bool = False


@dataclass
class SubscriptionInfo:
    """订阅信息"""
    subscription_id: str
    user_id: str
    license_type: LicenseType
    status: SubscriptionStatus
    start_date: str
    end_date: str
    auto_renew: bool = True
    payment_method: str = ""
    amount: float = 0.0
    currency: str = "USD"


class LicensingSystem:
    """许可证管理系统"""
    
    def __init__(self, api_url: str = "https://license.scene-weaver.com/api"):
        self.api_url = api_url
        self.local_license_file = Path("config/license.json")
        self.logger = logging.getLogger(__name__)
        
        # 本地许可证缓存
        self.cached_license: Optional[LicenseInfo] = None
        self._load_local_license()
    
    def _load_local_license(self):
        """加载本地许可证"""
        try:
            if self.local_license_file.exists():
                with open(self.local_license_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 处理枚举类型反序列化
                    if 'license_type' in data:
                        data['license_type'] = LicenseType(data['license_type'])
                    self.cached_license = self._parse_license_info(data)
                    self.logger.info("本地许可证加载成功")
        except Exception as e:
            self.logger.warning(f"本地许可证加载失败: {e}")
    
    def _save_local_license(self, license_info: LicenseInfo):
        """保存本地许可证"""
        try:
            self.local_license_file.parent.mkdir(parents=True, exist_ok=True)
            # 将数据类转换为字典并处理枚举类型
            license_dict = asdict(license_info)
            license_dict['license_type'] = license_info.license_type.value
            
            with open(self.local_license_file, 'w', encoding='utf-8') as f:
                json.dump(license_dict, f, indent=2, ensure_ascii=False)
            self.logger.info("本地许可证保存成功")
        except Exception as e:
            self.logger.error(f"本地许可证保存失败: {e}")
    
    def _parse_license_info(self, data: Dict[str, Any]) -> LicenseInfo:
        """解析许可证信息"""
        return LicenseInfo(
            license_key=data['license_key'],
            license_type=data['license_type'] if isinstance(data['license_type'], LicenseType) else LicenseType(data['license_type']),
            user_email=data['user_email'],
            user_name=data['user_name'],
            organization=data.get('organization', ''),
            issue_date=data.get('issue_date', ''),
            expiry_date=data.get('expiry_date', ''),
            max_devices=data.get('max_devices', 1),
            features=data.get('features', []),
            signature=data.get('signature', ''),
            is_valid=data.get('is_valid', False)
        )
    
    def activate_license(self, license_key: str, user_email: str = None) -> bool:
        """激活许可证"""
        try:
            data = {
                'license_key': license_key,
                'user_email': user_email or self._get_machine_id(),
                'machine_id': self._get_machine_id()
            }
            
            url = f"{self.api_url}/activate"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                license_data = result['license']
                license_info = self._parse_license_info(license_data)
                license_info.is_valid = True
                
                # 保存许可证
                self.cached_license = license_info
                self._save_local_license(license_info)
                
                self.logger.info(f"许可证激活成功: {license_key}")
                return True
            else:
                self.logger.error(f"许可证激活失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"许可证激活异常: {e}")
            return False
    
    def validate_license(self) -> bool:
        """验证当前许可证"""
        if not self.cached_license:
            return False
        
        try:
            # 检查过期时间
            if self.cached_license.expiry_date:
                expiry_date = datetime.fromisoformat(self.cached_license.expiry_date)
                if datetime.now() > expiry_date:
                    self.cached_license.is_valid = False
                    self.logger.warning("许可证已过期")
                    return False
            
            # 在线验证（可选）
            if self._should_online_verify():
                return self._online_verify()
            
            return self.cached_license.is_valid
            
        except Exception as e:
            self.logger.error(f"许可证验证失败: {e}")
            return False
    
    def _should_online_verify(self) -> bool:
        """判断是否需要在线验证"""
        # 可以根据时间间隔或其他条件决定
        return False  # 暂时禁用在线验证
    
    def _online_verify(self) -> bool:
        """在线验证许可证"""
        try:
            data = {
                'license_key': self.cached_license.license_key,
                'machine_id': self._get_machine_id()
            }
            
            url = f"{self.api_url}/verify"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            is_valid = result.get('valid', False)
            self.cached_license.is_valid = is_valid
            
            if not is_valid:
                self.logger.warning(f"在线验证失败: {result.get('error')}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"在线验证异常: {e}")
            return False
    
    def get_current_license(self) -> Optional[LicenseInfo]:
        """获取当前许可证信息"""
        return self.cached_license
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """检查功能是否启用"""
        if not self.cached_license or not self.cached_license.is_valid:
            return False
        
        # 免费版只允许基础功能
        if self.cached_license.license_type == LicenseType.FREE:
            free_features = ['basic_rendering', 'simple_effects']
            return feature_name in free_features
        
        # 其他版本检查功能列表
        return feature_name in self.cached_license.features
    
    def get_available_features(self) -> List[str]:
        """获取可用功能列表"""
        if not self.cached_license or not self.cached_license.is_valid:
            return ['basic_rendering']
        
        return self.cached_license.features
    
    def _get_machine_id(self) -> str:
        """获取机器标识"""
        try:
            # 简化的机器ID生成
            import platform
            machine_info = f"{platform.node()}_{platform.processor()}"
            return hashlib.sha256(machine_info.encode()).hexdigest()[:16]
        except Exception:
            return "unknown_machine"
    
    def deactivate_license(self) -> bool:
        """停用许可证"""
        if not self.cached_license:
            return True
        
        try:
            data = {
                'license_key': self.cached_license.license_key,
                'machine_id': self._get_machine_id()
            }
            
            url = f"{self.api_url}/deactivate"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                # 清除本地许可证
                self.cached_license = None
                if self.local_license_file.exists():
                    self.local_license_file.unlink()
                
                self.logger.info("许可证停用成功")
                return True
            else:
                self.logger.error(f"许可证停用失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"许可证停用异常: {e}")
            return False
    
    def get_license_info(self) -> Dict[str, Any]:
        """获取许可证详细信息"""
        if not self.cached_license:
            return {'status': 'no_license'}
        
        return {
            'status': 'valid' if self.cached_license.is_valid else 'invalid',
            'type': self.cached_license.license_type.value,
            'user': self.cached_license.user_name,
            'organization': self.cached_license.organization,
            'expiry_date': self.cached_license.expiry_date,
            'features': self.cached_license.features
        }


class SubscriptionSystem:
    """订阅管理系统"""
    
    def __init__(self, api_url: str = "https://subscribe.scene-weaver.com/api"):
        self.api_url = api_url
        self.local_sub_file = Path("config/subscription.json")
        self.logger = logging.getLogger(__name__)
        
        self.cached_subscription: Optional[SubscriptionInfo] = None
        self._load_local_subscription()
    
    def _load_local_subscription(self):
        """加载本地订阅信息"""
        try:
            if self.local_sub_file.exists():
                with open(self.local_sub_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cached_subscription = self._parse_subscription_info(data)
        except Exception as e:
            self.logger.warning(f"本地订阅加载失败: {e}")
    
    def _save_local_subscription(self, sub_info: SubscriptionInfo):
        """保存本地订阅信息"""
        try:
            self.local_sub_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.local_sub_file, 'w', encoding='utf-8') as f:
                json.dump(vars(sub_info), f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"本地订阅保存失败: {e}")
    
    def _parse_subscription_info(self, data: Dict[str, Any]) -> SubscriptionInfo:
        """解析订阅信息"""
        return SubscriptionInfo(
            subscription_id=data['subscription_id'],
            user_id=data['user_id'],
            license_type=LicenseType(data['license_type']),
            status=SubscriptionStatus(data['status']),
            start_date=data['start_date'],
            end_date=data['end_date'],
            auto_renew=data.get('auto_renew', True),
            payment_method=data.get('payment_method', ''),
            amount=float(data.get('amount', 0)),
            currency=data.get('currency', 'USD')
        )
    
    def create_subscription(self, user_id: str, license_type: LicenseType,
                          payment_token: str) -> bool:
        """创建订阅"""
        try:
            data = {
                'user_id': user_id,
                'license_type': license_type.value,
                'payment_token': payment_token,
                'auto_renew': True
            }
            
            url = f"{self.api_url}/subscriptions"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                sub_data = result['subscription']
                sub_info = self._parse_subscription_info(sub_data)
                self.cached_subscription = sub_info
                self._save_local_subscription(sub_info)
                
                self.logger.info(f"订阅创建成功: {sub_info.subscription_id}")
                return True
            else:
                self.logger.error(f"订阅创建失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"订阅创建异常: {e}")
            return False
    
    def cancel_subscription(self, subscription_id: str = None) -> bool:
        """取消订阅"""
        if not subscription_id and self.cached_subscription:
            subscription_id = self.cached_subscription.subscription_id
        
        if not subscription_id:
            return False
        
        try:
            url = f"{self.api_url}/subscriptions/{subscription_id}/cancel"
            req = urllib.request.Request(
                url,
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                if self.cached_subscription:
                    self.cached_subscription.status = SubscriptionStatus.CANCELLED
                    self._save_local_subscription(self.cached_subscription)
                
                self.logger.info("订阅取消成功")
                return True
            else:
                self.logger.error(f"订阅取消失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"订阅取消异常: {e}")
            return False
    
    def get_subscription_status(self) -> Optional[SubscriptionInfo]:
        """获取订阅状态"""
        return self.cached_subscription
    
    def is_subscription_active(self) -> bool:
        """检查订阅是否活跃"""
        if not self.cached_subscription:
            return False
        
        # 检查状态
        if self.cached_subscription.status != SubscriptionStatus.ACTIVE:
            return False
        
        # 检查有效期
        end_date = datetime.fromisoformat(self.cached_subscription.end_date)
        return datetime.now() < end_date
    
    def renew_subscription(self, payment_token: str) -> bool:
        """续订订阅"""
        if not self.cached_subscription:
            return False
        
        try:
            data = {
                'subscription_id': self.cached_subscription.subscription_id,
                'payment_token': payment_token
            }
            
            url = f"{self.api_url}/subscriptions/renew"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                sub_data = result['subscription']
                sub_info = self._parse_subscription_info(sub_data)
                self.cached_subscription = sub_info
                self._save_local_subscription(sub_info)
                
                self.logger.info("订阅续订成功")
                return True
            else:
                self.logger.error(f"订阅续订失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"订阅续订异常: {e}")
            return False


# 商业化系统主类
class CommerceSystem:
    """商业化系统主类"""
    
    def __init__(self):
        self.licensing = LicensingSystem()
        self.subscription = SubscriptionSystem()
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """初始化商业化系统"""
        try:
            # 验证许可证
            license_valid = self.licensing.validate_license()
            
            # 验证订阅
            subscription_active = self.subscription.is_subscription_active()
            
            self.logger.info(f"许可证状态: {'有效' if license_valid else '无效'}")
            self.logger.info(f"订阅状态: {'活跃' if subscription_active else '非活跃'}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"商业化系统初始化失败: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'license': self.licensing.get_license_info(),
            'subscription': {
                'active': self.subscription.is_subscription_active(),
                'info': vars(self.subscription.get_subscription_status()) if 
                       self.subscription.get_subscription_status() else None
            }
        }
    
    def is_commercial_feature_enabled(self, feature_name: str) -> bool:
        """检查商业功能是否启用"""
        # 优先检查订阅
        if self.subscription.is_subscription_active():
            return True
        
        # 检查许可证
        return self.licensing.is_feature_enabled(feature_name)
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """获取定价信息"""
        return {
            'free': {
                'price': 0,
                'features': ['basic_rendering', 'simple_effects'],
                'max_devices': 1
            },
            'personal': {
                'price': 29.99,
                'period': 'year',
                'features': ['advanced_rendering', 'particle_effects', 'custom_shaders'],
                'max_devices': 2
            },
            'professional': {
                'price': 99.99,
                'period': 'year',
                'features': ['all_personal_features', 'ai_integration', 'multiplayer', 'export_formats'],
                'max_devices': 5
            },
            'enterprise': {
                'price': '定制',
                'features': ['all_professional_features', 'dedicated_support', 'custom_development', 'on_premise'],
                'max_devices': -1  # unlimited
            }
        }


# 本地许可系统（用于开发测试）
class LocalLicensing(LicensingSystem):
    """本地许可系统"""
    
    def __init__(self):
        super().__init__("http://localhost:8080/api")
        self._init_default_license()
    
    def _init_default_license(self):
        """初始化默认许可证"""
        default_license = LicenseInfo(
            license_key="LOCAL_DEV_LICENSE",
            license_type=LicenseType.PROFESSIONAL,
            user_email="developer@localhost",
            user_name="Local Developer",
            issue_date=datetime.now().isoformat(),
            expiry_date=(datetime.now() + timedelta(days=365)).isoformat(),
            max_devices=10,
            features=['basic_rendering', 'advanced_rendering', 'particle_effects', 
                     'custom_shaders', 'ai_integration', 'multiplayer'],
            is_valid=True
        )
        
        self.cached_license = default_license
        self._save_local_license(default_license)
    
    def activate_license(self, license_key: str, user_email: str = None) -> bool:
        """本地许可证激活"""
        # 简化处理，总是返回成功
        self.logger.info("本地许可证激活成功")
        return True
    
    def validate_license(self) -> bool:
        """本地许可证验证"""
        return True if self.cached_license else False


# 商业系统工厂
class CommerceSystemFactory:
    """商业系统工厂"""
    
    @staticmethod
    def create_commerce_system(system_type: str = "online") -> CommerceSystem:
        """创建商业系统实例"""
        commerce = CommerceSystem()
        
        if system_type == "local":
            commerce.licensing = LocalLicensing()
        
        return commerce