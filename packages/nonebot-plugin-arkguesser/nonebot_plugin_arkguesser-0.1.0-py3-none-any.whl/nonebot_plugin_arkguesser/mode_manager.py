"""
模式管理器
负责管理游戏模式设置（兔头/大头）
"""

import json
from typing import Dict, Any
from pathlib import Path

class ModeManager:
    """模式管理器"""
    
    def __init__(self):
        self.settings_file = Path(__file__).parent / "resources" / "data" / "mode_settings.json"
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_settings()
    
    def _load_settings(self):
        """加载设置文件"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {}
        except Exception as e:
            print(f"加载模式设置失败: {e}")
            self.settings = {}
    
    def _save_settings(self):
        """保存设置文件"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模式设置失败: {e}")
    
    def get_mode(self, user_id: str = None, group_id: str = None) -> str:
        """获取当前模式设置"""
        # 优先级：群聊设置 > 个人设置 > 默认设置
        if group_id and group_id in self.settings.get("groups", {}):
            return self.settings["groups"][group_id]
        
        if user_id and user_id in self.settings.get("users", {}):
            return self.settings["users"][user_id]
        
        return self.settings.get("default", "大头")
    
    def set_mode(self, mode: str, user_id: str = None, group_id: str = None) -> Dict[str, Any]:
        """设置模式"""
        if mode not in ["兔头", "大头"]:
            return {
                "success": False,
                "message": "无效的模式，请选择 '兔头' 或 '大头'"
            }
        
        try:
            if group_id:
                # 群聊设置
                if "groups" not in self.settings:
                    self.settings["groups"] = {}
                self.settings["groups"][group_id] = mode
                scope = "群聊"
            elif user_id:
                # 个人设置
                if "users" not in self.settings:
                    self.settings["users"] = {}
                self.settings["users"][user_id] = mode
                scope = "个人"
            else:
                # 默认设置
                self.settings["default"] = mode
                scope = "全局"
            
            self._save_settings()
            
            return {
                "success": True,
                "mode": mode,
                "scope": scope,
                "message": f"模式已设置为：{mode}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"设置失败：{str(e)}"
            }
    
    def reset_mode(self, user_id: str = None, group_id: str = None) -> Dict[str, Any]:
        """重置模式设置"""
        try:
            if group_id and "groups" in self.settings:
                if group_id in self.settings["groups"]:
                    del self.settings["groups"][group_id]
                    scope = "群聊"
                else:
                    return {
                        "success": False,
                        "message": "群聊未设置自定义模式"
                    }
            elif user_id and "users" in self.settings:
                if user_id in self.settings["users"]:
                    del self.settings["users"][user_id]
                    scope = "个人"
                else:
                    return {
                        "success": False,
                        "message": "个人未设置自定义模式"
                    }
            else:
                # 重置默认设置
                self.settings["default"] = "大头"
                scope = "全局"
            
            self._save_settings()
            
            return {
                "success": True,
                "mode": self.get_mode(user_id, group_id),
                "scope": scope,
                "message": "模式已重置"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"重置失败：{str(e)}"
            }
    
    def get_mode_info(self, user_id: str = None, group_id: str = None) -> Dict[str, Any]:
        """获取模式信息"""
        current_mode = self.get_mode(user_id, group_id)
        
        if group_id and group_id in self.settings.get("groups", {}):
            source = "群聊设置"
        elif user_id and user_id in self.settings.get("users", {}):
            source = "个人设置"
        else:
            source = "默认设置"
        
        return {
            "mode": current_mode,
            "source": source,
            "description": self._get_mode_description(current_mode)
        }
    
    def _get_mode_description(self, mode: str) -> str:
        """获取模式描述"""
        descriptions = {
            "大头": "标准难度模式，使用标准立绘，适合正常的游戏体验",
            "兔头": "趣味模式，使用兔头立绘，增加游戏的趣味性和挑战性"
        }
        return descriptions.get(mode, "未知模式")

# 创建全局实例
mode_manager = ModeManager()
