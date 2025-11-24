# yuepao_game_ui/main.py - 修复版
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
import os
import sys

# 添加上级目录到Python路径，以便导入后端模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 尝试导入游戏模块
try:
    from game import Game
    from player import Player
    from skills import SkillSystem
    import config
    GAME_MODULES_AVAILABLE = True
    print("成功导入游戏模块")
except ImportError as e:
    print(f"无法导入游戏模块: {e}")
    GAME_MODULES_AVAILABLE = False

# 设置窗口大小模拟手机屏幕 (9:16比例)
Window.size = (360, 640)

# 角色数据 - 使用config.py中的数据
try:
    CHARACTERS = []
    for char_id, char_data in config.CHARACTERS.items():
        CHARACTERS.append({
            "id": char_id,
            "name": char_data["name"],
            "faction": char_data["faction"],
            "hp": char_data["health"],
            "atk": char_data["attack"],
            "desc": char_data["desc"]
        })
except:
    # 如果导入config失败，使用硬编码数据
    CHARACTERS = [
        {"id": "1", "name": "GTY", "faction": "姜", "hp": 91, "atk": 13, 
         "desc": "越草越勇：每次行动后攻击力永久翻倍"},
        {"id": "2", "name": "NSY", "faction": "燕", "hp": 55, "atk": 40,
         "desc": "以草作层：攻击成功增加层数(每层+15攻，最多4层)，被攻击减少层数，血量≤30时减伤50%"},
        {"id": "3", "name": "FHF", "faction": "姜", "hp": 200, "atk": 20,
         "desc": "变换姿态：血量≥100时攻击力+50%且受到伤害翻倍，血量≤50时攻击力-50%且受到伤害减半"},
        {"id": "4", "name": "WYB", "faction": "俞", "hp": 150, "atk": 8,
         "desc": "扩肛：任何角色受到伤害时，可对攻击者发起猜拳，赢则获得2个招，输则受到15点伤害并获得1个招；入肛：消耗5个招进入招草状态，指定至多3人只能攻击你，招草状态下减伤50%，每受击减少1招，招清零则退出招草状态"},
        {"id": "5", "name": "CQL", "faction": "俞", "hp": 80, "atk": 25,
         "desc": "双头青龙：当场上有其他角色造成伤害时，你可以选择一名其他角色发起猜拳，若你赢，则你对该角色造成25点伤害，若他赢，其对你造成25点伤害"},
        {"id": "6", "name": "NSB", "faction": "汤", "hp": 87, "atk": 25,
         "desc": "牛头人：当场上有其他角色造成伤害时，你可以选择对受击者额外造成15伤害，该技能每发动一次，该伤害提高3点（本场游戏中永久提升）"},
        {"id": "7", "name": "NHB", "faction": "姜", "hp": 150, "atk": 150,
         "desc": "慢性养胃：攻击力始终等于当前生命值；前两次攻击不造成伤害，第三次攻击只能造成50％的伤害，后续攻击正常"},
        {"id": "8", "name": "ZXW", "faction": "姜", "hp": 78, "atk": 21,
         "desc": "肾宝片：当你行动时，可以放弃这次行动并回复35点生命；攻击力增加等同于已损失生命值的数值（血量降低会使攻击增加，血量恢复不会使攻击降低）"}
    ]

# 主菜单界面
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # 游戏标题
        title = Label(
            text='月抛大作战',
            font_size=40,
            font_name='SimHei',
            size_hint=(1, 0.3)
        )
        layout.add_widget(title)
        
        # 开始游戏按钮
        start_btn = Button(
            text='开始游戏',
            font_size=24,
            font_name='SimHei',
            size_hint=(1, 0.2)
        )
        start_btn.bind(on_press=self.go_to_player_count)
        layout.add_widget(start_btn)
        
        # 退出游戏按钮
        exit_btn = Button(
            text='退出游戏', 
            font_size=24,
            font_name='SimHei',
            size_hint=(1, 0.2)
        )
        exit_btn.bind(on_press=self.exit_game)
        layout.add_widget(exit_btn)
        
        self.add_widget(layout)
    
    def go_to_player_count(self, instance):
        self.manager.current = 'player_count'
    
    def exit_game(self, instance):
        App.get_running_app().stop()

# 玩家人数选择界面
class PlayerCountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """构建玩家人数选择界面"""
        layout = BoxLayout(orientation='vertical', padding=50, spacing=30)
        
        # 标题
        title = Label(
            text='选择玩家人数',
            font_size=32,
            font_name='SimHei',
            size_hint=(1, 0.3)
        )
        layout.add_widget(title)
        
        # 玩家人数选择按钮
        buttons_layout = GridLayout(cols=2, spacing=20, size_hint=(1, 0.6))
        
        for i in range(2, 9):  # 2-8个玩家
            btn = Button(
                text=f'{i} 人游戏',
                font_size=20,
                font_name='SimHei'
            )
            btn.player_count = i
            btn.bind(on_press=self.select_player_count)
            buttons_layout.add_widget(btn)
        
        layout.add_widget(buttons_layout)
        
        # 返回按钮
        back_btn = Button(
            text='返回主菜单',
            font_size=20,
            font_name='SimHei',
            size_hint=(1, 0.1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def select_player_count(self, instance):
        """选择玩家人数并进入角色选择"""
        player_count = instance.player_count
        character_screen = self.manager.get_screen('character_select')
        character_screen.setup_multiplayer(player_count)
        self.manager.current = 'character_select'
    
    def go_back(self, instance):
        """返回主菜单"""
        self.manager.current = 'main_menu'

# 角色选择界面（支持多玩家选择）
class CharacterSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 角色数据
        self.characters = CHARACTERS
        self.selected_characters = []  # 存储多个选择的角色
        self.current_player_index = 0  # 当前正在选择的玩家索引
        self.total_players = 1  # 总玩家数，默认为1
        self.current_preview_char = None  # 当前预览的角色
        
        # 主布局 - 使用BoxLayout垂直排列
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题区域 (5%)
        self.title_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
        
        # 返回按钮
        back_btn = Button(
            text='←',
            font_size=24,
            font_name='SimHei',
            size_hint=(0.2, 1)
        )
        back_btn.bind(on_press=self.go_back)
        self.title_layout.add_widget(back_btn)
        
        # 标题
        self.title_label = Label(
            text='选择角色 - 玩家1',
            font_size=24,
            font_name='SimHei',
            size_hint=(0.6, 1)
        )
        self.title_layout.add_widget(self.title_label)
        
        # 占位空间
        placeholder = Label(size_hint=(0.2, 1))
        self.title_layout.add_widget(placeholder)
        
        main_layout.add_widget(self.title_layout)
        
        # 角色立绘区域 (60%) - 占据大部分空间
        self.character_image_area = BoxLayout(
            orientation='vertical', 
            size_hint=(1, 0.6)
        )
        
        # 默认立绘显示 - 使用Image部件
        self.character_image = Image(
            source='assets/images/characters/default.png',  # 默认图片
            size_hint=(1, 1),
            allow_stretch=True,  # 允许拉伸
            keep_ratio=True      # 保持比例
        )
        
        self.character_image_area.add_widget(self.character_image)
        main_layout.add_widget(self.character_image_area)
        
        # 角色信息区域 (10%)
        info_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        # 角色名称和势力
        self.name_label = Label(
            text='未选择角色',
            font_size=20,
            font_name='SimHei',
            size_hint=(0.5, 1)
        )
        info_layout.add_widget(self.name_label)
        
        # 角色属性
        self.stats_label = Label(
            text='',
            font_size=16,
            font_name='SimHei',
            size_hint=(0.5, 1)
        )
        info_layout.add_widget(self.stats_label)
        
        main_layout.add_widget(info_layout)
        
        # 已选择角色显示区域 (10%)
        self.selected_chars_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.selected_chars_scroll = ScrollView(size_hint=(1, 1))
        self.selected_chars_grid = GridLayout(cols=8, spacing=5, size_hint_x=None)
        self.selected_chars_grid.bind(minimum_width=self.selected_chars_grid.setter('width'))
        self.selected_chars_scroll.add_widget(self.selected_chars_grid)
        self.selected_chars_layout.add_widget(self.selected_chars_scroll)
        main_layout.add_widget(self.selected_chars_layout)
        
        # 角色选择区域 (15%) - 底部横向滚动
        selection_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.15))
        
        # 角色选择滚动区域
        scroll_view = ScrollView(size_hint=(1, 0.7))
        self.character_grid = GridLayout(
            cols=8,  # 8个角色，一行显示
            spacing=5,
            size_hint_x=None
        )
        self.character_grid.bind(minimum_width=self.character_grid.setter('width'))
        
        # 添加角色选择按钮
        for char in self.characters:
            char_btn = Button(
                text=char['name'],
                font_name='SimHei',
                font_size=16,
                size_hint_x=None,
                width=70  # 固定宽度
            )
            
            # 绑定点击事件
            char_btn.char_data = char
            char_btn.bind(on_press=self.select_character)
            
            self.character_grid.add_widget(char_btn)
        
        scroll_view.add_widget(self.character_grid)
        selection_layout.add_widget(scroll_view)
        
        # 操作按钮区域
        self.action_buttons = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=10)
        
        # 详细信息按钮
        details_btn = Button(
            text='详细信息',
            font_size=18,
            font_name='SimHei'
        )
        details_btn.bind(on_press=self.show_details)
        self.action_buttons.add_widget(details_btn)
        
        # 确认选择按钮
        self.confirm_btn = Button(
            text='确认选择',
            font_size=18,
            font_name='SimHei'
        )
        self.confirm_btn.bind(on_press=self.confirm_selection)
        self.confirm_btn.disabled = True  # 初始禁用
        self.action_buttons.add_widget(self.confirm_btn)
        
        # 开始游戏按钮
        self.start_btn = Button(
            text='开始游戏',
            font_size=18,
            font_name='SimHei'
        )
        self.start_btn.bind(on_press=self.start_game)
        self.start_btn.disabled = True  # 初始禁用
        self.action_buttons.add_widget(self.start_btn)
        
        selection_layout.add_widget(self.action_buttons)
        main_layout.add_widget(selection_layout)
        
        self.add_widget(main_layout)
    
    def setup_multiplayer(self, player_count):
        """设置多玩家选择模式"""
        self.total_players = player_count
        self.current_player_index = 0
        self.selected_characters = []
        self.current_preview_char = None
        self.update_title()
        self.update_selected_chars_display()
        self.confirm_btn.disabled = True
        self.start_btn.disabled = True
        
        # 重置角色按钮颜色
        self.clear_selection_color()
    
    def update_title(self):
        """更新标题显示当前选择的玩家"""
        if self.current_player_index < self.total_players:
            self.title_label.text = f'选择角色 - 玩家{self.current_player_index + 1}'
        else:
            self.title_label.text = '所有玩家已选择完成'
    
    def update_selected_chars_display(self):
        """更新已选择角色显示"""
        self.selected_chars_grid.clear_widgets()
        
        for i, char in enumerate(self.selected_characters):
            char_label = Label(
                text=f'P{i+1}:{char["name"]}',
                font_size=12,
                font_name='SimHei',
                size_hint_x=None,
                width=60
            )
            self.selected_chars_grid.add_widget(char_label)
        
        # 添加空位显示
        for i in range(len(self.selected_characters), self.total_players):
            empty_label = Label(
                text=f'P{i+1}:未选',
                font_size=12,
                font_name='SimHei',
                color=(0.5, 0.5, 0.5, 1),  # 灰色显示
                size_hint_x=None,
                width=60
            )
            self.selected_chars_grid.add_widget(empty_label)
    
    def select_character(self, instance):
        """选择角色（多玩家模式）"""
        if self.current_player_index >= self.total_players:
            return  # 所有玩家已选择完成
        
        selected_char = instance.char_data
        
        # 更新预览角色
        self.current_preview_char = selected_char
        
        # 更新立绘和角色信息
        self.update_character_display(selected_char)
        
        # 启用确认按钮
        self.confirm_btn.disabled = False
        
        # 高亮显示选中的角色按钮
        self.clear_selection_color()
        instance.background_color = (0, 1, 0, 1)  # 绿色背景
        
        print(f"预览角色: {selected_char['name']}")
    
    def update_character_display(self, char):
        """更新角色显示（立绘和信息）"""
        if not char:
            return
            
        char_name = char['name']
        
        # 更新立绘
        image_path = f'assets/images/characters/{char_name}.png'
        
        # 检查图片文件是否存在
        if os.path.exists(image_path):
            self.character_image.source = image_path
        else:
            # 如果图片不存在，使用默认图片或显示占位符
            self.character_image.source = 'assets/images/characters/default.png'
            print(f"警告: 角色 {char_name} 的立绘图片不存在: {image_path}")
        
        # 更新角色信息
        self.name_label.text = f"{char['name']}-{char['faction']}"
        self.stats_label.text = f"HP:{char['hp']} ATK:{char['atk']}"
    
    def clear_selection_color(self):
        """清除所有角色按钮的选择颜色"""
        for child in self.character_grid.children:
            if hasattr(child, 'char_data'):
                child.background_color = (1, 1, 1, 1)  # 白色背景
    
    def show_details(self, instance):
        """显示角色详细信息弹窗"""
        char_to_show = None
        
        # 如果有预览角色，显示预览角色的信息
        if self.current_preview_char:
            char_to_show = self.current_preview_char
        # 否则显示已选择角色的信息
        elif self.selected_characters and self.current_player_index > 0:
            char_to_show = self.selected_characters[self.current_player_index - 1]
        else:
            self.show_error_popup("未选择角色", "请先选择一个角色")
            return
        
        # 创建详细信息内容 - 使用相对单位确保适配不同屏幕
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        
        # 角色基本信息
        info_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        
        name_label = Label(
            text=f"{char_to_show['name']}-{char_to_show['faction']}",
            font_size=dp(20),
            font_name='SimHei',
            size_hint=(0.6, 1)
        )
        info_layout.add_widget(name_label)
        
        stats_label = Label(
            text=f"HP:{char_to_show['hp']}\nATK:{char_to_show['atk']}",
            font_size=dp(16),
            font_name='SimHei',
            size_hint=(0.4, 1)
        )
        info_layout.add_widget(stats_label)
        
        content.add_widget(info_layout)
        
        # 技能描述（可滚动）- 修复文字显示不全问题
        desc_scroll = ScrollView(
            size_hint=(1, 0.7),
            do_scroll_x=False,  # 禁用水平滚动
            do_scroll_y=True    # 启用垂直滚动
        )
        
        # 创建一个容器来确保文本正确换行
        desc_container = BoxLayout(orientation='vertical', size_hint_y=None)
        desc_container.bind(minimum_height=desc_container.setter('height'))
        
        desc_label = Label(
            text=char_to_show['desc'],
            font_size=dp(16),
            font_name='SimHei',
            size_hint_y=None,
            text_size=(dp(320), None),  # 设置固定宽度确保正确换行
            halign='left',
            valign='top',
            padding=(dp(5), dp(5))  # 添加内边距确保文字不贴边
        )
        
        # 绑定文本高度，确保ScrollView可以正确滚动
        desc_label.bind(
            texture_size=lambda inst, val: setattr(desc_label, 'height', val[1])
        )
        
        desc_container.add_widget(desc_label)
        desc_scroll.add_widget(desc_container)
        content.add_widget(desc_scroll)
        
        # 关闭按钮
        close_btn = Button(
            text='关闭',
            font_size=dp(18),
            font_name='SimHei',
            size_hint=(1, 0.1)
        )
        content.add_widget(close_btn)
        
        # 创建弹窗 - 修复标题乱码问题
        popup = Popup(
            title=f'{char_to_show["name"]}技能详情',
            title_size=dp(20),
            title_font='SimHei',  # 设置标题字体
            content=content,
            size_hint=(0.9, 0.85),  # 稍微调大一点，确保有足够空间
            auto_dismiss=False
        )
        
        # 延迟调整文本大小，确保在布局完成后
        Clock.schedule_once(lambda dt: self.adjust_text_size(desc_label, popup), 0.1)
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def adjust_text_size(self, label, popup):
        """调整文本大小以适应弹窗宽度"""
        # 获取弹窗内容区域的实际宽度
        content_width = popup.content.width - dp(30)  # 减去内边距
        
        # 更新文本宽度
        label.text_size = (content_width, None)
        
        # 强制重新计算纹理
        label.texture_update()
    
    def confirm_selection(self, instance):
        """确认当前选择"""
        if not self.current_preview_char:
            self.show_error_popup("未选择角色", "请先选择一个角色")
            return
        
        # 检查角色是否已被选择
        if self.current_preview_char in self.selected_characters:
            self.show_error_popup("角色重复", f"角色 {self.current_preview_char['name']} 已被选择，请选择其他角色")
            return
        
        # 添加到已选择列表
        if len(self.selected_characters) <= self.current_player_index:
            self.selected_characters.append(self.current_preview_char)
        else:
            self.selected_characters[self.current_player_index] = self.current_preview_char
        
        # 更新当前玩家索引
        self.current_player_index += 1
        self.current_preview_char = None
        
        # 禁用确认按钮
        self.confirm_btn.disabled = True
        
        # 更新显示
        self.update_title()
        self.update_selected_chars_display()
        
        # 重置立绘显示
        self.character_image.source = 'assets/images/characters/default.png'
        self.name_label.text = '未选择角色'
        self.stats_label.text = ''
        
        # 清除角色按钮颜色
        self.clear_selection_color()
        
        # 如果所有玩家都选择了角色，启用开始游戏按钮
        if self.current_player_index >= self.total_players:
            self.start_btn.disabled = False
        
        print(f"玩家{self.current_player_index}确认选择了角色")
    
    def start_game(self, instance):
        """开始游戏"""
        if len(self.selected_characters) < self.total_players:
            self.show_error_popup("选择未完成", f"还有{self.total_players - len(self.selected_characters)}个玩家未选择角色")
            return
        
        # 检查游戏模块是否可用
        if not GAME_MODULES_AVAILABLE:
            self.show_error_popup("游戏模块加载失败", "无法加载游戏逻辑模块，请检查game.py、player.py、skills.py和config.py文件是否存在。")
            return
            
        # 跳转到游戏界面
        game_screen = self.manager.get_screen('game')
        game_screen.start_game(self.selected_characters)
        self.manager.current = 'game'
    
    def show_error_popup(self, title, message):
        """显示错误弹窗"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        label = Label(
            text=message,
            font_size=16,
            font_name='SimHei'
        )
        content.add_widget(label)
        
        close_btn = Button(
            text='关闭',
            font_size=16,
            font_name='SimHei'
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def go_back(self, instance):
        """返回玩家人数选择界面"""
        self.manager.current = 'player_count'

# 游戏主界面
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = None
        self.selected_characters = []
        self.zhaocao_targets = []  # WYB技能目标选择
        self.current_popup = None  # 当前打开的弹窗
        self.build_ui()
    
    def build_ui(self):
        """构建游戏主界面"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 顶部信息栏
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.08))
        
        # 返回按钮
        back_btn = Button(
            text='←',
            font_size=20,
            font_name='SimHei',
            size_hint=(0.15, 1)
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        # 回合信息
        self.turn_label = Label(
            text='回合: 0',
            font_size=18,
            font_name='SimHei',
            size_hint=(0.7, 1)
        )
        top_bar.add_widget(self.turn_label)
        
        # 当前玩家
        self.current_player_label = Label(
            text='当前: 无',
            font_size=16,
            font_name='SimHei',
            size_hint=(0.15, 1)
        )
        top_bar.add_widget(self.current_player_label)
        
        main_layout.add_widget(top_bar)
        
        # 玩家状态区域
        player_status_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        # 玩家状态标题
        status_title = Label(
            text='玩家状态',
            font_size=18,
            font_name='SimHei',
            size_hint=(1, 0.2)
        )
        player_status_layout.add_widget(status_title)
        
        # 玩家状态滚动区域
        self.player_scroll = ScrollView(size_hint=(1, 0.8))
        self.player_grid = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.player_grid.bind(minimum_height=self.player_grid.setter('height'))
        self.player_scroll.add_widget(self.player_grid)
        player_status_layout.add_widget(self.player_scroll)
        
        main_layout.add_widget(player_status_layout)
        
        # 行动按钮区域
        action_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=10)
        
        # 行动按钮
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.6), spacing=10)
        
        self.attack_btn = Button(
            text='攻击',
            font_size=18,
            font_name='SimHei'
        )
        self.attack_btn.bind(on_press=self.show_attack_targets)
        btn_layout.add_widget(self.attack_btn)
        
        self.skill_btn = Button(
            text='使用技能',
            font_size=18,
            font_name='SimHei'
        )
        self.skill_btn.bind(on_press=self.use_skill)
        btn_layout.add_widget(self.skill_btn)
        
        self.end_turn_btn = Button(
            text='结束回合',
            font_size=18,
            font_name='SimHei'
        )
        self.end_turn_btn.bind(on_press=self.end_turn)
        btn_layout.add_widget(self.end_turn_btn)
        
        action_layout.add_widget(btn_layout)
        
        # 状态信息
        self.action_label = Label(
            text='请选择行动',
            font_size=14,
            font_name='SimHei',
            size_hint=(1, 0.4)
        )
        action_layout.add_widget(self.action_label)
        
        main_layout.add_widget(action_layout)
        
        # 战斗日志区域
        log_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        
        log_title = Label(
            text='战斗日志',
            font_size=16,
            font_name='SimHei',
            size_hint=(1, 0.15)
        )
        log_layout.add_widget(log_title)
        
        self.log_scroll = ScrollView(size_hint=(1, 0.85))
        self.log_layout_inner = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None
        )
        self.log_layout_inner.bind(minimum_height=self.log_layout_inner.setter('height'))
        self.log_scroll.add_widget(self.log_layout_inner)
        log_layout.add_widget(self.log_scroll)
        
        main_layout.add_widget(log_layout)
        
        self.add_widget(main_layout)
    
    def start_game(self, selected_characters):
        """开始游戏，初始化后端游戏逻辑"""
        try:
            self.selected_characters = selected_characters
            self.game = Game()
            
            # 添加玩家到游戏
            for i, char_data in enumerate(selected_characters, 1):
                self.game.add_player(i, char_data["name"], char_data["atk"], char_data["hp"], char_data["faction"])
            
            # 设置队伍（自由对战模式）
            for i in range(1, len(selected_characters) + 1):
                self.game.teams[i] = [i]
            
            # 初始化UI状态
            self.update_ui()
            self.add_log("游戏开始！")
            
            # 显示剪刀石头布界面决定第一个行动玩家
            self.show_rps_selection()
                
        except Exception as e:
            self.add_log(f"游戏初始化错误: {str(e)}")
            print(f"游戏初始化错误: {e}")
    
    def show_rps_selection(self):
        """显示剪刀石头布选择界面"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title = Label(
            text='剪刀石头布 - 选择行动玩家',
            font_size=20,
            font_name='SimHei',
            size_hint=(1, 0.2)
        )
        content.add_widget(title)
        
        # 玩家列表
        players_layout = GridLayout(cols=1, spacing=5, size_hint=(1, 0.6))
        
        alive_players = []
        for player_id, player in self.game.players.items():
            if player.is_alive:
                alive_players.append((player_id, player))
                player_btn = Button(
                    text=f'玩家{player_id}[{player.name}] HP:{player.health}',
                    font_size=16,
                    font_name='SimHei'
                )
                player_btn.player_id = player_id
                player_btn.bind(on_press=self.select_current_player)
                players_layout.add_widget(player_btn)
        
        # 如果没有存活玩家，显示游戏结束
        if not alive_players:
            no_players_label = Label(
                text='没有存活玩家，游戏结束',
                font_size=16,
                font_name='SimHei'
            )
            players_layout.add_widget(no_players_label)
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(players_layout)
        content.add_widget(scroll_view)
        
        # 说明文本
        desc_label = Label(
            text="请在现实中进行剪刀石头布，然后选择胜者",
            font_size=14,
            font_name='SimHei',
            size_hint=(1, 0.1)
        )
        content.add_widget(desc_label)
        
        popup = Popup(
            title='决定行动顺序',
            title_font='SimHei',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        
        self.current_popup = popup
        popup.open()
    
    def select_current_player(self, instance):
        """选择当前行动玩家"""
        player_id = instance.player_id
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None
        
        self.game.set_current_player(player_id)
        self.update_ui()
        self.add_log(f"剪刀石头布胜者: 玩家{player_id}")
        self.add_log(f"轮到玩家{player_id}行动")
    
    def update_ui(self):
        """更新UI显示"""
        if not self.game:
            return
            
        # 更新回合信息
        self.turn_label.text = f'回合: {self.game.turn_count}'
        
        # 更新当前玩家
        if self.game.current_player:
            current_player = self.game.players[self.game.current_player]
            self.current_player_label.text = f'P{self.game.current_player}'
            
            # 更新行动按钮状态
            is_alive = current_player.is_alive
            self.attack_btn.disabled = not is_alive
            self.skill_btn.disabled = not is_alive
            self.end_turn_btn.disabled = not is_alive
            
            if not is_alive:
                self.action_label.text = "当前玩家已死亡"
            else:
                self.action_label.text = f"玩家{self.game.current_player}[{current_player.name}]的回合"
        else:
            self.current_player_label.text = '无'
            self.action_label.text = '请选择行动'
        
        # 更新玩家状态
        self.player_grid.clear_widgets()
        for player_id, player in self.game.players.items():
            status_color = (0, 1, 0, 1) if player.is_alive else (1, 0, 0, 1)  # 绿色存活，红色死亡
            
            # 创建玩家状态标签
            player_text = f"玩家{player_id}[{player.name}] HP:{player.health}/{player.max_health} ATK:{player.attack}"
            
            # 显示特殊状态
            if player.name == "NSY" and hasattr(player, 'layers'):
                player_text += f" 层数:{player.layers}"
            elif player.name == "WYB":
                state = "招草" if hasattr(player, 'in_zhaocao') and player.in_zhaocao else "正常"
                player_text += f" 招数:{player.zhao_count} ({state})"
            elif player.name == "NSB" and hasattr(player, 'extra_damage'):
                player_text += f" 额外伤害:{player.extra_damage}"
            elif player.name == "NHB" and hasattr(player, 'attack_count'):
                attack_type = "无伤害" if player.attack_count < 2 else "半伤害" if player.attack_count == 2 else "正常"
                player_text += f" 攻击阶段:{attack_type}"
            elif player.name == "ZXW" and hasattr(player, 'max_lost_health'):
                player_text += f" 损失加成:{player.max_lost_health}"
            
            if player_id == self.game.current_player:
                player_text = "➤ " + player_text  # 标记当前玩家
            
            player_label = Label(
                text=player_text,
                font_size=14,
                font_name='SimHei',
                size_hint_y=None,
                height=40,
                color=status_color
            )
            self.player_grid.add_widget(player_label)
    
    def add_log(self, message):
        """添加战斗日志"""
        log_label = Label(
            text=message,
            font_size=12,
            font_name='SimHei',
            size_hint_y=None,
            height=30,
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        log_label.bind(texture_size=log_label.setter('size'))
        self.log_layout_inner.add_widget(log_label)
        
        # 自动滚动到底部
        def scroll_to_bottom(dt):
            self.log_scroll.scroll_y = 0
        Clock.schedule_once(scroll_to_bottom, 0.1)
    
    def show_attack_targets(self, instance):
        """显示攻击目标选择"""
        if not self.game or not self.game.current_player:
            self.add_log("错误：没有当前玩家")
            return
            
        current_player = self.game.players[self.game.current_player]
        if not current_player.is_alive:
            self.add_log("错误：当前玩家已死亡")
            return
        
        # 创建目标选择弹窗
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        title = Label(
            text='选择攻击目标:',
            font_size=18,
            font_name='SimHei',
            size_hint=(1, 0.2)
        )
        content.add_widget(title)
        
        # 目标列表
        targets_layout = GridLayout(cols=1, spacing=5, size_hint=(1, 0.7))
        
        valid_targets = []
        for target_id, target in self.game.players.items():
            if (target_id != self.game.current_player and 
                target.is_alive and
                self.is_valid_target(self.game.current_player, target_id)):
                
                valid_targets.append((target_id, target))
                
                target_btn = Button(
                    text=f'玩家{target_id}[{target.name}] HP:{target.health}',
                    font_size=14,
                    font_name='SimHei'
                )
                target_btn.target_id = target_id
                target_btn.bind(on_press=self.execute_attack)
                targets_layout.add_widget(target_btn)
        
        if not valid_targets:
            no_targets_label = Label(
                text='没有可攻击的目标',
                font_size=16,
                font_name='SimHei'
            )
            targets_layout.add_widget(no_targets_label)
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(targets_layout)
        content.add_widget(scroll_view)
        
        # 取消按钮
        cancel_btn = Button(
            text='取消',
            font_size=16,
            font_name='SimHei',
            size_hint=(1, 0.1)
        )
        content.add_widget(cancel_btn)
        
        popup = Popup(
            title='攻击目标',
            title_font='SimHei',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        
        # 将popup对象传递给按钮，以便在execute_attack中关闭
        for child in targets_layout.children:
            if hasattr(child, 'target_id'):
                child.popup = popup
        
        cancel_btn.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()
    
    def is_valid_target(self, attacker_id, target_id):
        """检查目标是否有效（考虑WYB的招草状态等限制）"""
        attacker = self.game.players[attacker_id]
        target = self.game.players[target_id]
        
        # 检查WYB的招草状态限制
        for player in self.game.players.values():
            if (player.name == "WYB" and hasattr(player, 'in_zhaocao') and 
                player.in_zhaocao and hasattr(player, 'zhaocao_targets') and
                attacker_id in player.zhaocao_targets and
                target_id != player.player_id):
                return False
                
        return True
    
    def execute_attack(self, instance):
        """执行攻击"""
        target_id = instance.target_id
        
        # 先关闭弹窗
        if hasattr(instance, 'popup'):
            instance.popup.dismiss()
            self.current_popup = None
        
        # 保存游戏状态
        self.game.save_state(f"玩家{self.game.current_player}攻击玩家{target_id}")
        
        success = self.game.attack(target_id)
        
        if success:
            attacker = self.game.players[self.game.current_player]
            target = self.game.players[target_id]
            self.add_log(f"玩家{self.game.current_player}[{attacker.name}] 攻击了 玩家{target_id}[{target.name}]！")
            
            # 检查目标是否死亡
            if not target.is_alive:
                self.add_log(f"玩家{target_id}[{target.name}] 被击败了！")
        else:
            self.add_log("攻击失败")
            
        self.update_ui()
        
        # 检查游戏是否结束
        game_over, winners = self.game.check_game_over()
        if game_over:
            self.show_game_over(winners)
        else:
            # 显示剪刀石头布选择下一个玩家
            Clock.schedule_once(lambda dt: self.show_rps_selection(), 1.0)
    
    def use_skill(self, instance):
        """使用技能"""
        if not self.game or not self.game.current_player:
            self.add_log("错误：没有当前玩家")
            return
            
        current_player = self.game.players[self.game.current_player]
        if not current_player.is_alive:
            self.add_log("错误：当前玩家已死亡")
            return
        
        # 根据角色名称调用不同的技能界面
        if current_player.name == "WYB":
            self.use_wyb_skill(current_player)
        elif current_player.name == "ZXW":
            self.use_zxw_skill(current_player)
        elif current_player.name == "GTY":
            self.add_log("GTY技能为被动触发，无需主动使用")
        elif current_player.name == "NSY":
            self.add_log("NSY技能为被动触发，无需主动使用")
        elif current_player.name == "FHF":
            self.add_log("FHF技能为被动触发，无需主动使用")
        elif current_player.name == "CQL":
            self.add_log("CQL技能为被动触发，无需主动使用")
        elif current_player.name == "NSB":
            self.add_log("NSB技能为被动触发，无需主动使用")
        elif current_player.name == "NHB":
            self.add_log("NHB技能为被动触发，无需主动使用")
        else:
            self.add_log(f"{current_player.name}没有可主动使用的技能")
    
    def use_wyb_skill(self, player):
        """WYB技能使用界面"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title = Label(
            text='WYB技能选择',
            font_size=20,
            font_name='SimHei',
            size_hint=(1, 0.2)
        )
        content.add_widget(title)
        
        # 技能描述
        desc_label = Label(
            text="入肛：消耗5个招进入招草状态，指定至多3人只能攻击你",
            font_size=14,
            font_name='SimHei',
            size_hint=(1, 0.3),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        desc_label.bind(texture_size=desc_label.setter('size'))
        content.add_widget(desc_label)
        
        # 当前招数显示
        zhao_label = Label(
            text=f"当前招数: {player.zhao_count}",
            font_size=16,
            font_name='SimHei',
            size_hint=(1, 0.1)
        )
        content.add_widget(zhao_label)
        
        # 技能使用按钮
        if player.zhao_count >= 5 and not player.in_zhaocao:
            skill_btn = Button(
                text='使用入肛技能 (消耗5招)',
                font_size=16,
                font_name='SimHei',
                size_hint=(1, 0.2)
            )
            skill_btn.bind(on_press=lambda x: self.execute_wyb_skill(player, popup))
            content.add_widget(skill_btn)
        else:
            if player.in_zhaocao:
                status_label = Label(
                    text='已在招草状态中',
                    font_size=16,
                    font_name='SimHei',
                    size_hint=(1, 0.2)
                )
                content.add_widget(status_label)
            else:
                status_label = Label(
                    text=f'招数不足，需要5招，当前只有{player.zhao_count}招',
                    font_size=16,
                    font_name='SimHei',
                    size_hint=(1, 0.2)
                )
                content.add_widget(status_label)
        
        # 取消按钮
        cancel_btn = Button(
            text='取消',
            font_size=16,
            font_name='SimHei',
            size_hint=(1, 0.1)
        )
        content.add_widget(cancel_btn)
        
        popup = Popup(
            title='WYB技能',
            title_font='SimHei',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()
    
    def execute_wyb_skill(self, player, popup):
        """执行WYB技能"""
        # 关闭技能选择弹窗
        popup.dismiss()
        self.current_popup = None
        
        # 选择招草状态的目标
        self.select_zhaocao_targets(player)
    
    def select_zhaocao_targets(self, player):
        """选择招草状态的目标"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title = Label(
            text='选择招草状态目标 (至多3人)',
            font_size=18,
            font_name='SimHei',
            size_hint=(1, 0.15)
        )
        content.add_widget(title)
        
        # 目标列表
        targets_layout = GridLayout(cols=1, spacing=5, size_hint=(1, 0.7))
        
        self.zhaocao_targets = []  # 存储选中的目标
        
        for target_id, target in self.game.players.items():
            if target_id != player.player_id and target.is_alive:
                target_btn = ToggleButton(
                    text=f'玩家{target_id}[{target.name}] HP:{target.health}',
                    font_size=14,
                    font_name='SimHei',
                    group='zhaocao_targets'
                )
                target_btn.target_id = target_id
                target_btn.bind(on_press=self.toggle_zhaocao_target)
                targets_layout.add_widget(target_btn)
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(targets_layout)
        content.add_widget(scroll_view)
        
        # 按钮区域
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        confirm_btn = Button(
            text='确认选择',
            font_size=16,
            font_name='SimHei'
        )
        confirm_btn.bind(on_press=lambda x: self.finalize_wyb_skill(player, popup2))
        btn_layout.add_widget(confirm_btn)
        
        cancel_btn = Button(
            text='取消',
            font_size=16,
            font_name='SimHei'
        )
        cancel_btn.bind(on_press=popup2.dismiss)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup2 = Popup(
            title='选择招草目标',
            title_font='SimHei',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        
        cancel_btn.popup = popup2
        confirm_btn.popup = popup2
        self.current_popup = popup2
        popup2.open()
    
    def toggle_zhaocao_target(self, instance):
        """切换招草目标选择"""
        if instance.state == 'down':
            if len(self.zhaocao_targets) < 3:
                self.zhaocao_targets.append(instance.target_id)
            else:
                instance.state = 'normal'
                self.show_error_popup("选择限制", "最多只能选择3个目标")
        else:
            if instance.target_id in self.zhaocao_targets:
                self.zhaocao_targets.remove(instance.target_id)
    
    def finalize_wyb_skill(self, player, popup):
        """最终确定WYB技能使用"""
        # 关闭目标选择弹窗
        popup.dismiss()
        self.current_popup = None
        
        # 执行技能
        player.zhao_count -= 5
        player.in_zhaocao = True
        player.zhaocao_targets = self.zhaocao_targets[:3]  # 确保不超过3个
        
        self.add_log(f"WYB使用入肛技能，进入招草状态")
        if player.zhaocao_targets:
            self.add_log(f"招草状态目标: {player.zhaocao_targets}")
        else:
            self.add_log("未选择任何目标")
        
        # 保存游戏状态
        self.game.save_state(f"玩家{player.player_id}使用WYB技能")
        
        self.update_ui()
        
        # 显示剪刀石头布选择下一个玩家
        Clock.schedule_once(lambda dt: self.show_rps_selection(), 1.0)
    
    def use_zxw_skill(self, player):
        """ZXW技能使用界面"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title = Label(
            text='ZXW技能选择',
            font_size=20,
            font_name='SimHei',
            size_hint=(1, 0.2)
        )
        content.add_widget(title)
        
        # 技能描述
        desc_label = Label(
            text="肾宝片：放弃本次行动并回复35点生命",
            font_size=16,
            font_name='SimHei',
            size_hint=(1, 0.3)
        )
        content.add_widget(desc_label)
        
        # 当前状态显示
        status_label = Label(
            text=f"当前HP: {player.health}/{player.max_health}",
            font_size=16,
            font_name='SimHei',
            size_hint=(1, 0.1)
        )
        content.add_widget(status_label)
        
        # 技能使用按钮
        skill_btn = Button(
            text='使用肾宝片技能',
            font_size=16,
            font_name='SimHei',
            size_hint=(1, 0.2)
        )
        skill_btn.bind(on_press=lambda x: self.execute_zxw_skill(player, popup))
        content.add_widget(skill_btn)
        
        # 取消按钮
        cancel_btn = Button(
            text='取消',
            font_size=16,
            font_name='SimHei',
            size_hint=(1, 0.1)
        )
        content.add_widget(cancel_btn)
        
        popup = Popup(
            title='ZXW技能',
            title_font='SimHei',
            content=content,
            size_hint=(0.7, 0.5),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()
    
    def execute_zxw_skill(self, player, popup):
        """执行ZXW技能"""
        # 关闭技能选择弹窗
        popup.dismiss()
        self.current_popup = None
        
        # 执行技能
        old_health = player.health
        player.health = min(player.health + 35, player.max_health)
        
        # 记录已损失生命值（用于攻击力计算）
        if not hasattr(player, 'max_lost_health'):
            player.max_lost_health = 0
            
        current_lost = player.max_health - player.health
        if current_lost > player.max_lost_health:
            player.max_lost_health = current_lost
        
        self.add_log(f"ZXW使用肾宝片技能，回复35点生命 (HP: {old_health} → {player.health})")
        
        # 保存游戏状态
        self.game.save_state(f"玩家{player.player_id}使用ZXW技能")
        
        self.update_ui()
        
        # 显示剪刀石头布选择下一个玩家
        Clock.schedule_once(lambda dt: self.show_rps_selection(), 1.0)
    
    def end_turn(self, instance):
        """结束当前回合"""
        if not self.game:
            return
            
        self.add_log(f"玩家{self.game.current_player}结束了回合")
        
        # 显示剪刀石头布选择下一个玩家
        self.show_rps_selection()
    
    def show_game_over(self, winners):
        """显示游戏结束画面"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        if winners:
            if len(winners) == 1:
                title_text = f"玩家{winners[0].player_id}[{winners[0].name}]获胜！"
            else:
                title_text = "队伍获胜！"
        else:
            title_text = "游戏结束！无人获胜"
        
        title = Label(
            text=title_text,
            font_size=24,
            font_name='SimHei',
            size_hint=(1, 0.3)
        )
        content.add_widget(title)
        
        # 显示获胜者
        winners_text = "\n".join([f"玩家{p.player_id}[{p.name}]" for p in winners]) if winners else "无"
        winners_label = Label(
            text=winners_text,
            font_size=18,
            font_name='SimHei',
            size_hint=(1, 0.4)
        )
        content.add_widget(winners_label)
        
        # 按钮
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=10)
        
        restart_btn = Button(
            text='重新开始',
            font_size=18,
            font_name='SimHei'
        )
        restart_btn.bind(on_press=self.restart_game)
        btn_layout.add_widget(restart_btn)
        
        menu_btn = Button(
            text='返回主菜单',
            font_size=18,
            font_name='SimHei'
        )
        menu_btn.bind(on_press=self.go_to_main_menu)
        btn_layout.add_widget(menu_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='游戏结束',
            title_font='SimHei',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        restart_btn.popup = popup
        menu_btn.popup = popup
        self.current_popup = popup
        popup.open()
    
    def restart_game(self, instance):
        """重新开始游戏"""
        instance.popup.dismiss()
        self.current_popup = None
        self.start_game(self.selected_characters)
    
    def go_to_main_menu(self, instance):
        """返回主菜单"""
        instance.popup.dismiss()
        self.current_popup = None
        self.manager.current = 'main_menu'
    
    def go_back(self, instance):
        """返回角色选择界面"""
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None
        self.manager.current = 'character_select'
    
    def show_error_popup(self, title, message):
        """显示错误弹窗"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        label = Label(
            text=message,
            font_size=16,
            font_name='SimHei'
        )
        content.add_widget(label)
        
        close_btn = Button(
            text='关闭',
            font_size=16,
            font_name='SimHei'
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            title_font='SimHei',
            content=content,
            size_hint=(0.6, 0.3),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()

# 主应用
class YuepaoGameApp(App):
    def build(self):
        self.title = '月抛大作战'
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加屏幕
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(PlayerCountScreen(name='player_count'))
        sm.add_widget(CharacterSelectScreen(name='character_select'))
        sm.add_widget(GameScreen(name='game'))
        
        return sm

if __name__ == '__main__':
    YuepaoGameApp().run()
