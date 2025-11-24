# player.py - 玩家类定义（添加新角色属性）
from skills import SkillSystem

class Player:
    """玩家类"""
    def __init__(self, player_id, name, attack, health, faction):
        self.player_id = player_id
        self.name = name
        self.base_attack = attack
        self.attack = attack
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.faction = faction
        self.skill_system = SkillSystem()
        
        # 初始化角色特定属性
        self.init_character_attributes()
    
    def init_character_attributes(self):
        """初始化角色特定属性"""
        if self.name == "NSY":
            self.layers = 0
        elif self.name == "WYB":
            self.zhao_count = 0
            self.in_zhaocao = False
            self.zhaocao_targets = []
        elif self.name == "NSB":
            self.extra_damage = 15  # 初始额外伤害值
        elif self.name == "NHB":
            self.attack_count = 0  # 攻击次数计数
            # NHB的攻击力初始等于生命值
            self.attack = self.health
            self.base_attack = self.health
        elif self.name == "ZXW":
            self.max_lost_health = 0  # 最大损失生命值
    
    def take_damage(self, damage, attacker=None, game=None):
        """受到伤害，考虑技能效果"""
        actual_damage = damage
        
        # 调用技能系统的伤害计算
        if self.name in self.skill_system.skill_handlers and "take_damage_calc" in self.skill_system.skill_handlers[self.name]:
            actual_damage, message = self.skill_system.skill_handlers[self.name]["take_damage_calc"](self, damage)
            if message:
                print(message)
        
        old_health = self.health
        self.health -= actual_damage
        
        # 调用生命值变化技能（NHB）
        if self.name in self.skill_system.skill_handlers and "on_health_change" in self.skill_system.skill_handlers[self.name]:
            result = self.skill_system.skill_handlers[self.name]["on_health_change"](self, old_health, self.health)
            if result:
                print(result)
        
        # 调用技能系统的受伤害处理
        if self.name in self.skill_system.skill_handlers and "on_take_damage" in self.skill_system.skill_handlers[self.name]:
            result = self.skill_system.skill_handlers[self.name]["on_take_damage"](self, attacker)
            if result:
                print(result)
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
        
        return actual_damage
    
    def after_action(self):
        """行动后触发的被动技能"""
        if self.name in self.skill_system.skill_handlers and "after_action" in self.skill_system.skill_handlers[self.name]:
            result = self.skill_system.skill_handlers[self.name]["after_action"](self)
            if result:
                print(result)
    
    def on_attack_success(self):
        """攻击成功时触发的技能"""
        if self.name in self.skill_system.skill_handlers and "on_attack_success" in self.skill_system.skill_handlers[self.name]:
            result = self.skill_system.skill_handlers[self.name]["on_attack_success"](self)
            if result:
                print(result)
    
    def on_any_damage(self, attacker, target, game):
        """任何角色受到伤害时触发的技能"""
        if self.name in self.skill_system.skill_handlers and "on_any_damage" in self.skill_system.skill_handlers[self.name]:
            result = self.skill_system.skill_handlers[self.name]["on_any_damage"](self, attacker, target, game)
            return result
        return None
    
    def on_other_damage(self, attacker, target, game):
        """其他角色造成伤害时触发的技能（CQL, NSB）"""
        if self.name in self.skill_system.skill_handlers and "on_other_damage" in self.skill_system.skill_handlers[self.name]:
            result = self.skill_system.skill_handlers[self.name]["on_other_damage"](self, attacker, target, game)
            return result
        return None
    
    def use_skill(self, game=None):
        """使用主动技能"""
        if self.name in self.skill_system.skill_handlers and "use_skill" in self.skill_system.skill_handlers[self.name]:
            result = self.skill_system.skill_handlers[self.name]["use_skill"](self, game)
            if result:
                print(result)
                return True
        else:
            print(f"{self.name}没有可主动使用的技能")
        return False
    
    def turn_start(self):
        """回合开始时触发的技能"""
        if self.name in self.skill_system.skill_handlers and "turn_start" in self.skill_system.skill_handlers[self.name]:
            result = self.skill_system.skill_handlers[self.name]["turn_start"](self)
            if result:
                print(result)
    
    def reset_turn(self):
        """重置回合状态"""
        if self.name in self.skill_system.skill_handlers and "reset_turn" in self.skill_system.skill_handlers[self.name]:
            self.skill_system.skill_handlers[self.name]["reset_turn"](self)
    
    def attack_calc(self, damage):
        """攻击伤害计算（考虑技能效果）"""
        if self.name in self.skill_system.skill_handlers and "attack_calc" in self.skill_system.skill_handlers[self.name]:
            actual_damage, message = self.skill_system.skill_handlers[self.name]["attack_calc"](self, damage)
            if message:
                print(message)
            return actual_damage
        return damage
    
    def __str__(self):
        """显示玩家信息"""
        status = "存活" if self.is_alive else "死亡"
        attack_info = f"{self.attack}" if self.attack == self.base_attack else f"{self.attack}(基础{self.base_attack})"
        
        # 显示NSY的层数
        if self.name == "NSY" and hasattr(self, 'layers'):
            return f"玩家{self.player_id}[{self.name}-{self.faction}] HP:{self.health}/{self.max_health} ATK:{attack_info} 层数:{self.layers} ({status})"
        
        # 显示WYB的招数和状态
        if self.name == "WYB":
            state = "招草" if self.in_zhaocao else "正常"
            return f"玩家{self.player_id}[{self.name}-{self.faction}] HP:{self.health}/{self.max_health} ATK:{attack_info} 招数:{self.zhao_count} ({state})"
        
        # 显示NSB的额外伤害
        if self.name == "NSB" and hasattr(self, 'extra_damage'):
            return f"玩家{self.player_id}[{self.name}-{self.faction}] HP:{self.health}/{self.max_health} ATK:{attack_info} 额外伤害:{self.extra_damage} ({status})"
        
        # 显示NHB的攻击计数
        if self.name == "NHB" and hasattr(self, 'attack_count'):
            attack_type = "无伤害" if self.attack_count < 2 else "半伤害" if self.attack_count == 2 else "正常"
            return f"玩家{self.player_id}[{self.name}-{self.faction}] HP:{self.health}/{self.max_health} ATK:{attack_info} 攻击阶段:{attack_type}({self.attack_count}次) ({status})"
        
        # 显示ZXW的损失生命值加成
        if self.name == "ZXW" and hasattr(self, 'max_lost_health'):
            return f"玩家{self.player_id}[{self.name}-{self.faction}] HP:{self.health}/{self.max_health} ATK:{attack_info} 损失加成:{self.max_lost_health} ({status})"
        
        return f"玩家{self.player_id}[{self.name}-{self.faction}] HP:{self.health}/{self.max_health} ATK:{attack_info} ({status})"
