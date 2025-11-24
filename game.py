# game.py - 游戏管理器（完整版本）
from player import Player
import config
import copy

class Game:
    """游戏管理器"""
    def __init__(self):
        self.players = {}
        self.current_player = None
        self.turn_count = 0
        self.available_characters = config.CHARACTERS
        self.teams = {}
        self.history = []
        self.last_action = None
    
    def save_state(self, action_description):
        """保存当前游戏状态"""
        state = {
            'players': {pid: copy.deepcopy(player) for pid, player in self.players.items()},
            'current_player': self.current_player,
            'turn_count': self.turn_count,
            'teams': copy.deepcopy(self.teams),
            'action': action_description
        }
        self.history.append(state)
        if len(self.history) > 10:
            self.history.pop(0)
    
    def undo(self):
        """撤回上一步操作"""
        if len(self.history) < 2:
            print("无法撤回，历史记录不足")
            return False
        
        current = self.history.pop()
        previous = self.history[-1]
        
        self.players = previous['players']
        self.current_player = previous['current_player']
        self.turn_count = previous['turn_count']
        self.teams = previous['teams']
        
        print(f"已撤回: {current['action']}")
        self.show_all_players()
        return True
    
    def show_character_list(self):
        """显示可用角色列表"""
        print("\n" + "="*50)
        print("可用角色列表:")
        print("="*50)
        for key, char in self.available_characters.items():
            print(f"{key}. {char['name']}-{char['faction']} - HP:{char['health']} ATK:{char['attack']}")
            print(f"   技能: {char['desc']}")
            print()
    
    def setup_teams(self, num_players):
        """设置队伍"""
        print("\n=== 队伍设置 ===")
        
        while True:
            team_mode = input("是否启用组队模式? (y/n): ").lower()
            if team_mode in ['y', 'n']:
                break
            else:
                print("请输入 y 或 n")
        
        if team_mode == 'n':
            for i in range(1, num_players + 1):
                self.teams[i] = [i]
            return
        
        while True:
            try:
                num_teams = int(input(f"请输入队伍数量 (2-{num_players}): "))
                if 2 <= num_teams <= num_players:
                    break
                else:
                    print(f"队伍数量必须在2-{num_players}之间")
            except ValueError:
                print("请输入有效数字")
        
        team_assignments = {}
        remaining_players = list(range(1, num_players + 1))
        
        for team_id in range(1, num_teams + 1):
            while True:
                try:
                    print(f"\n队伍 {team_id} 分配")
                    print(f"剩余玩家: {remaining_players}")
                    team_size = int(input("请输入本队人数: "))
                    
                    if 1 <= team_size <= len(remaining_players) - (num_teams - team_id):
                        break
                    else:
                        print(f"队伍人数必须在1-{len(remaining_players) - (num_teams - team_id)}之间")
                except ValueError:
                    print("请输入有效数字")
            
            team_assignments[team_id] = []
            for _ in range(team_size):
                while True:
                    try:
                        player_id = int(input("选择玩家编号加入本队: "))
                        if player_id in remaining_players:
                            team_assignments[team_id].append(player_id)
                            remaining_players.remove(player_id)
                            break
                        else:
                            print("无效的玩家编号")
                    except ValueError:
                        print("请输入有效数字")
            
            print(f"队伍 {team_id}: {team_assignments[team_id]}")
        
        self.teams = team_assignments
    
    def setup_players(self):
        """设置玩家人数和角色"""
        print(config.GAME_INTRO)
        
        while True:
            try:
                num_players = int(input(f"请输入玩家人数 ({config.MIN_PLAYERS}-{config.MAX_PLAYERS}人): "))
                if config.MIN_PLAYERS <= num_players <= config.MAX_PLAYERS:
                    break
                else:
                    print(f"玩家人数必须在{config.MIN_PLAYERS}-{config.MAX_PLAYERS}之间！")
            except ValueError:
                print("请输入有效的数字！")
        
        self.setup_teams(num_players)
        
        print("\n=== 队伍分配结果 ===")
        for team_id, members in self.teams.items():
            print(f"队伍 {team_id}: {members}")
        
        self.show_character_list()
        
        for i in range(1, num_players + 1):
            while True:
                try:
                    print(f"\n--- 玩家{i}的角色选择 ---")
                    choice = input("请选择角色 (输入数字1-8): ")
                    
                    if choice in self.available_characters:
                        char_data = self.available_characters[choice]
                        self.add_player(i, char_data["name"], char_data["attack"], char_data["health"], char_data["faction"])
                        print(f"玩家{i} 选择了 {char_data['name']}-{char_data['faction']}")
                        break
                    else:
                        print("无效选择！请输入1-8之间的数字。")
                except Exception as e:
                    print(f"输入错误: {e}")
        
        print("\n游戏设置完成！")
        self.save_state("游戏开始")
    
    def add_player(self, player_id, name, attack, health, faction):
        """添加玩家"""
        new_player = Player(player_id, name, attack, health, faction)
        self.players[player_id] = new_player
    
    def show_all_players(self):
        """显示所有玩家状态"""
        print("\n" + "="*50)
        print("当前玩家状态:")
        print("="*50)
        
        for team_id, members in self.teams.items():
            print(f"\n队伍 {team_id}:")
            for player_id in members:
                if player_id in self.players:
                    print(f"  {self.players[player_id]}")
    
    def set_current_player(self, player_id):
        """设置当前行动的玩家"""
        if player_id in self.players:
            self.current_player = player_id
            player = self.players[player_id]
            
            for p in self.players.values():
                p.reset_turn()
            
            # 调用回合开始技能
            player.turn_start()
            
            print(f"\n玩家{player_id}[{player.name}]开始行动！")
            return True
        else:
            print("玩家不存在！")
            return False
    
    def attack(self, target_id):
        """攻击目标"""
        if self.current_player is None:
            print("请先设置当前行动玩家！")
            return False
        
        if target_id not in self.players:
            print("目标玩家不存在！")
            return False
        
        attacker = self.players[self.current_player]
        target = self.players[target_id]
        
        if not attacker.is_alive:
            print("攻击者已经死亡，无法行动！")
            return False
        
        if not target.is_alive:
            print("目标已经死亡，无法攻击！")
            return False
        
        if attacker.player_id == target.player_id:
            print("不能攻击自己！")
            return False
        
        # 检查WYB的招草状态限制
        for player in self.players.values():
            if (player.name == "WYB" and player.in_zhaocao and 
                self.current_player in player.zhaocao_targets and
                target.player_id != player.player_id):
                print(f"玩家{self.current_player}处于WYB的招草状态，只能攻击WYB！")
                return False
        
        self.save_state(f"玩家{self.current_player}攻击玩家{target_id}")
        
        # 计算攻击伤害（考虑技能效果）
        base_damage = attacker.attack
        actual_base_damage = attacker.attack_calc(base_damage)
        
        original_health = target.health
        actual_damage = target.take_damage(actual_base_damage, attacker, self)
        
        print(f"\n攻击结果:")
        print(f"玩家{self.current_player}[{attacker.name}] 攻击了 玩家{target_id}[{target.name}]！")
        print(f"造成 {actual_damage} 点伤害 (HP: {original_health} → {target.health})")
        
        # 攻击者攻击成功技能
        attacker.on_attack_success()
        
        # 攻击者行动后技能
        attacker.after_action()
        
        # 任何角色受伤害时触发的技能（如WYB的扩肛）
        for player in self.players.values():
            if player.is_alive:
                result = player.on_any_damage(attacker, target, self)
                if result and isinstance(result, dict) and result["type"] == "wyb_lost":
                    # 处理WYB猜拳失败的情况
                    player.take_damage(result["damage"], result["attacker"], self)
                elif result:
                    print(result)
        
        # 其他角色造成伤害时触发的技能（CQL, NSB）
        for player in self.players.values():
            if player.is_alive and player != attacker:  # 排除攻击者自己
                result = player.on_other_damage(attacker, target, self)
                if result:
                    print(result)
        
        if not target.is_alive:
            print(f"玩家{target_id}[{target.name}] 被击败了！")
        
        return True
    
    def check_game_over(self):
        """检查游戏是否结束"""
        # 检查是否有队伍获胜
        alive_teams = set()
        for team_id, members in self.teams.items():
            team_alive = any(self.players[pid].is_alive for pid in members if pid in self.players)
            if team_alive:
                alive_teams.add(team_id)
        
        if len(alive_teams) <= 1:
            if alive_teams:
                winning_team = list(alive_teams)[0]
                winning_players = [self.players[pid] for pid in self.teams[winning_team] 
                                 if pid in self.players and self.players[pid].is_alive]
                return True, winning_players
            else:
                return True, []  # 所有玩家都死亡
        return False, []
