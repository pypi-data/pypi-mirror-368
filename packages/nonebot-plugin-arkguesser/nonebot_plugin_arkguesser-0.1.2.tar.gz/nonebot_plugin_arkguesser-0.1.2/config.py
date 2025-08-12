from nonebot import get_driver
from typing import Dict, Any

class Config:
    """插件配置类"""
    
    def __init__(self):
        self.arkguesser_max_attempts: int = 10
        self.arkguesser_default_rarity_range: str = "6"
        self.arkguesser_default_mode: str = "大头"
        # 移除这里的 _load_config() 调用，避免在模块导入时就执行
    
    def _load_config(self):
        """从环境变量加载配置"""
        try:
            driver = get_driver()
            if hasattr(driver, 'config') and driver.config:
                # 使用 getattr 安全地访问配置属性，而不是使用 .get() 方法
                self.arkguesser_max_attempts = int(getattr(driver.config, "arkguesser_max_attempts", 10))
                self.arkguesser_default_rarity_range = str(getattr(driver.config, "arkguesser_default_rarity_range", "6"))
                self.arkguesser_default_mode = str(getattr(driver.config, "arkguesser_default_mode", "大头"))
        except Exception:
            # 如果配置加载失败，使用默认值，不影响插件正常运行
            pass

# 创建一个配置实例，但不立即加载配置
plugin_config = Config()

# 提供一个函数来确保配置已加载
def get_plugin_config():
    """获取插件配置，确保配置已加载"""
    plugin_config._load_config()
    return plugin_config