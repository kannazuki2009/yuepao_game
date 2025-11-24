# skills.py - 技能系统模块（完整版本）
import random

class SkillSystem:
    """技能系统管理器"""
    
    def __init__(self):
        self.skill_handlers = {}
        self.setup_skill_handlers()
    
    def setup_skill_handlers(self):
        """设置技能处理器"""
        # GTY - 越草越勇
        self.skill_handlers["GTY"] = {
            "after_action": self.gty_after_action,
            "reset_turn": self.gty_reset_turn
        }
        
        # NSY - 以草作层
        self.skill_handlers["NSY"] = {
            "on_attack_success": self.nsy_on_attack_success,
            "on_take_damage": self.nsy_on_take_damage,
            "take_damage_calc": self.nsy_take_damage_calc
        }
        
        # FHF - 变换姿态
        self.skill_handlers["FHF"] = {
            "turn_start": self.fhf_turn_start,
            "take_damage_calc": self.fhf_take_damage_calc
        }
        
        # WYB - 扩肛/入肛
        self.skill_handlers["WYB"] = {
            "on_any_damage": self.wyb_on_any_damage,
            "use_skill": self.wyb_use_skill,
            "take_damage_calc": self.wyb_take_damage_calc,
            "on_take_damage": self.wyb_on_take_damage
        }
        
        # CQL - 双头青龙
        self.skill_handlers["CQL"] = {
            "on_other_damage": self.cql_on_other_damage
        }
        
        # NSB - 牛头人
        self.skill_handlers["NSB"] = {
            "on_other_damage": self.nsb_on_other_damage
        }
        
        # NHB - 慢性养胃
        self.skill_handlers["NHB"] = {
            "on_health_change": self.nhb_on_health_change,
            "attack_calc": self.nhb_attack_calc,
            "on_attack_success": self.nhb_on_attack_success
        }
        
        # ZXW - 肾宝片
        self.skill_handlers["ZXW"] = {
            "use_skill": self.zxw_use_skill,
            "turn_start": self.zxw_turn_start,
            "attack_calc": self.zxw_attack_calc
        }
    
    # ===== GTY 技能实现 =====
    def gty_after_action(self, player):
        """GTY - 越草越勇：行动后攻击力翻倍"""
        old_attack = player.attack
        player.attack *= 2
        player.base_attack = player.attack
        return f"GTY技能【越草越勇】发动！攻击力从{old_attack}变为{player.attack}"
    
    def gty_reset_turn(self, player):
        """GTY - 回合重置（无效果，因为攻击力提升是永久的）"""
        pass
    
    # ===== NSY 技能实现 =====
    def nsy_on_attack_success(self, player):
        """NSY - 攻击成功时增加层数"""
        if hasattr(player, 'layers'):
            player.layers = min(player.layers + 1, 4)
            player.attack = player.base_attack + (player.layers * 15)
            return f"NSY技能【以草作层】触发！层数:{player.layers}, 攻击力:{player.attack}"
        return None
    
    def nsy_on_take_damage(self, player, attacker):
        """NSY - 被攻击时减少层数"""
        if hasattr(player, 'layers') and player.layers > 0:
            old_layers = player.layers
            player.layers -= 1
            player.attack = player.base_attack + (player.layers * 15)
            return f"NSY被攻击，层数减少: {old_layers} → {player.layers}, 攻击力: {player.attack}"
        return None
    
    def nsy_take_damage_calc(self, player, damage):
        """NSY - 血量≤30时减伤50%"""
        if player.health <= 30:
            return damage * 0.5, "NSY技能：血量≤30，受到伤害减半！"
        return damage, None
    
    # ===== FHF 技能实现 =====
    def fhf_turn_start(self, player):
        """FHF - 回合开始时根据血量调整攻击力"""
        old_attack = player.attack
        if player.health >= 100:
            player.attack = int(player.base_attack * 1.5)
        elif player.health <= 50:
            player.attack = int(player.base_attack * 0.5)
        else:
            player.attack = player.base_attack
        
        if old_attack != player.attack:
            return f"FHF姿态变化！攻击力从{old_attack}变为{player.attack}"
        return None
    
    def fhf_take_damage_calc(self, player, damage):
        """FHF - 根据血量调整受到的伤害"""
        if player.health >= 100:
            return damage * 2, "FHF姿态：血量≥100，受到伤害翻倍！"
        elif player.health <= 50:
            return damage * 0.5, "FHF姿态：血量≤50，受到伤害减半！"
        return damage, None
    
    # ===== WYB 技能实现 =====
    def wyb_on_any_damage(self, player, attacker, target, game):
        """WYB - 任何角色受到伤害时触发猜拳"""
        if player.is_alive and attacker != player:
            print(f"\nWYB技能【扩肛】触发！")
            print(f"请在现实中与攻击者玩家{attacker.player_id}进行猜拳")
            
            while True:
                try:
                    result = input("猜拳结果 (输入'W'表示WYB赢，输入'L'表示WYB输): ").upper()
                    if result in ['W', 'L']:
                        break
                    else:
                        print("请输入'W'或'L'")
                except:
                    print("输入错误，请重新输入")
            
            if result == 'W':
                old_zhao = player.zhao_count
                player.zhao_count += 2
                return f"WYB猜拳获胜！获得2个招 ({old_zhao} → {player.zhao_count})"
            else:
                old_zhao = player.zhao_count
                player.zhao_count += 1
                # 这里需要处理WYB受到伤害，但为了避免循环调用，我们返回一个标记
                return {"type": "wyb_lost", "damage": 15, "attacker": attacker}
        return None
    
    def wyb_use_skill(self, player, game):
        """WYB - 使用入肛技能进入招草状态"""
        if player.zhao_count >= 5 and not player.in_zhaocao:
            player.zhao_count -= 5
            player.in_zhaocao = True
            
            print("请选择至多3个目标（输入玩家编号，用空格分隔，不选则直接回车）:")
            alive_players = [str(pid) for pid, p in game.players.items() 
                           if p.is_alive and p.player_id != player.player_id]
            print(f"可选目标: {', '.join(alive_players)}")
            
            try:
                target_input = input("目标选择: ").strip()
                if target_input:
                    target_ids = [int(x) for x in target_input.split()]
                    player.zhaocao_targets = [tid for tid in target_ids 
                                          if tid in game.players and 
                                          game.players[tid].is_alive and
                                          tid != player.player_id][:3]
                    
                    return f"招草状态目标设置为: {player.zhaocao_targets}"
                else:
                    return "未选择任何目标"
            except ValueError:
                return "输入格式错误，未设置目标"
        elif player.in_zhaocao:
            return "WYB已在招草状态中"
        else:
            return f"WYB技能【入肛】需要至少5招，当前只有{player.zhao_count}招"
    
    def wyb_take_damage_calc(self, player, damage):
        """WYB - 招草状态下减伤50%"""
        if player.in_zhaocao:
            return damage * 0.5, "WYB招草状态：受到伤害减半！"
        return damage, None
    
    def wyb_on_take_damage(self, player, attacker):
        """WYB - 招草状态下每受击减少1招"""
        if player.in_zhaocao and attacker:
            old_zhao = player.zhao_count
            player.zhao_count = max(0, player.zhao_count - 1)
            result = f"WYB招草状态：受击减少1招 ({old_zhao} → {player.zhao_count})"
            
            if player.zhao_count == 0:
                player.in_zhaocao = False
                player.zhaocao_targets = []
                result += "\nWYB招草状态结束！"
            
            return result
        return None
    
    # ===== CQL 技能实现 =====
    def cql_on_other_damage(self, player, attacker, target, game):
        """CQL - 双头青龙：其他角色造成伤害时触发猜拳"""
        # 排除自己造成伤害的情况
        if player.is_alive and attacker != player:
            print(f"\nCQL技能【双头青龙】触发！")
            print(f"请在现实中与其他角色进行猜拳")
            
            # 选择猜拳目标
            alive_players = [str(pid) for pid, p in game.players.items() 
                           if p.is_alive and p.player_id != player.player_id]
            print(f"可选目标: {', '.join(alive_players)}")
            
            try:
                target_id = int(input("选择猜拳目标编号: "))
                if target_id not in game.players or not game.players[target_id].is_alive or target_id == player.player_id:
                    print("无效的目标选择")
                    return None
            except ValueError:
                print("输入格式错误")
                return None
            
            # 询问猜拳结果
            while True:
                try:
                    result = input("猜拳结果 (输入'W'表示CQL赢，输入'L'表示CQL输): ").upper()
                    if result in ['W', 'L']:
                        break
                    else:
                        print("请输入'W'或'L'")
                except:
                    print("输入错误，请重新输入")
            
            if result == 'W':
                # CQL赢，对目标造成25点伤害
                target_player = game.players[target_id]
                original_health = target_player.health
                target_player.take_damage(25, player, game)
                return f"CQL猜拳获胜！对玩家{target_id}造成25点伤害 (HP: {original_health} → {target_player.health})"
            else:
                # CQL输，受到25点伤害
                original_health = player.health
                player.take_damage(25, game.players[target_id], game)
                return f"CQL猜拳失败！受到25点伤害 (HP: {original_health} → {player.health})"
        return None
    
    # ===== NSB 技能实现 =====
    def nsb_on_other_damage(self, player, attacker, target, game):
        """NSB - 牛头人：其他角色造成伤害时触发额外伤害"""
        # 排除自己造成伤害的情况
        if player.is_alive and attacker != player:
            print(f"\nNSB技能【牛头人】触发！")
            print(f"攻击者玩家{attacker.player_id}对玩家{target.player_id}造成了伤害")
            
            choice = input("是否对受击者额外造成伤害? (y/n): ").lower()
            if choice == 'y':
                # 初始化额外伤害值
                if not hasattr(player, 'extra_damage'):
                    player.extra_damage = 15
                
                # 造成额外伤害
                original_health = target.health
                target.take_damage(player.extra_damage, player, game)
                
                result = f"NSB对玩家{target.player_id}额外造成{player.extra_damage}点伤害 (HP: {original_health} → {target.health})"
                
                # 增加下次额外伤害值
                player.extra_damage += 3
                result += f"\n下次额外伤害提升为{player.extra_damage}点"
                
                return result
        return None
    
    # ===== NHB 技能实现 =====
    def nhb_on_health_change(self, player, old_health, new_health):
        """NHB - 慢性养胃：生命值变化时攻击力同步变化"""
        if not hasattr(player, 'attack_count'):
            player.attack_count = 0
            
        # 攻击力始终等于当前生命值
        player.attack = new_health
        player.base_attack = new_health
        
        return f"NHB生命值变化，攻击力同步为{new_health}"
    
    def nhb_attack_calc(self, player, damage):
        """NHB - 攻击伤害计算"""
        if not hasattr(player, 'attack_count'):
            player.attack_count = 0
            
        # 前两次攻击不造成伤害
        if player.attack_count < 2:
            player.attack_count += 1
            return 0, f"NHB技能：前两次攻击不造成伤害（第{player.attack_count}次攻击）"
        # 第三次攻击造成50%伤害
        elif player.attack_count == 2:
            player.attack_count += 1
            actual_damage = damage * 0.5
            return actual_damage, f"NHB技能：第三次攻击只造成50%伤害（{actual_damage}点）"
        # 后续攻击正常
        else:
            player.attack_count += 1
            return damage, None
    
    def nhb_on_attack_success(self, player):
        """NHB - 攻击成功时计数"""
        # 这个计数在nhb_attack_calc中已经处理，这里不需要额外处理
        pass
    
    # ===== ZXW 技能实现 =====
    def zxw_use_skill(self, player, game):
        """ZXW - 肾宝片：放弃行动回复生命"""
        print(f"ZXW发动技能【肾宝片】！")
        choice = input("是否放弃本次行动并回复35点生命? (y/n): ").lower()
        
        if choice == 'y':
            old_health = player.health
            player.health = min(player.health + 35, player.max_health)
            
            # 记录已损失生命值（用于攻击力计算）
            if not hasattr(player, 'max_lost_health'):
                player.max_lost_health = 0
                
            current_lost = player.max_health - player.health
            if current_lost > player.max_lost_health:
                player.max_lost_health = current_lost
            
            return f"ZXW放弃行动，回复35点生命 (HP: {old_health} → {player.health})"
        return "ZXW未使用技能"
    
    def zxw_turn_start(self, player):
        """ZXW - 回合开始时更新攻击力"""
        # 确保有最大损失生命值属性
        if not hasattr(player, 'max_lost_health'):
            player.max_lost_health = 0
            
        # 计算当前损失生命值
        current_lost = player.max_health - player.health
        if current_lost > player.max_lost_health:
            player.max_lost_health = current_lost
        
        # 攻击力 = 基础攻击力 + 最大损失生命值
        old_attack = player.attack
        player.attack = player.base_attack + player.max_lost_health
        
        if old_attack != player.attack:
            return f"ZXW攻击力变化：{old_attack} → {player.attack}（基础{player.base_attack}+损失{player.max_lost_health}）"
        return None
    
    def zxw_attack_calc(self, player, damage):
        """ZXW - 攻击伤害计算（包含损失生命值的加成）"""
        # 攻击力已经在turn_start中更新，这里直接返回伤害值
        return damage, None
