# 英文名：GameX 中文名：给姆叉
# 基于Pygame开发的游戏框架，提供角色管理、窗口控制、输入交互、音频处理等核心功能
import math
import os
import sys
import pygame

print("Welcome to GameX, a product developed using Pygame!")

# 游戏窗口对象（通过display.set_window初始化，存储Pygame的display表面）
screen = pygame.display.set_mode
# 游戏时钟对象（通过display.set_window初始化，用于控制游戏帧率）
clock = pygame.time.Clock
# 存储所有角色/绘图对象的列表，用于图层管理和渲染顺序控制（索引越小，渲染层级越低）
role_list = list()


def _draw_role(i):
    if isinstance(i, role):
        # 跳过无造型或设置为不显示的角色
        if i.sculpt_number is None or not i.show:
            return

        # 获取处理后的图像（缩放、旋转等）
        image = _get_image(i)

        # 计算绘制坐标：使图像中心与角色位置（position）对齐
        width, height = image.get_size()
        x = i.position.real_x - width * 0.5
        y = i.position.real_y - height * 0.5

        # 将处理后的图像绘制到屏幕
        screen.blit(image, (x, y))


def _draw_pen(i):
    if isinstance(i, pen):
        # 绘制绘图层（pen对象的图层为全屏表面，直接绘制在(0,0)位置）
        screen.blit(i.layer, (0, 0))


def _get_mask(i):
    if i.mask is None or i._staticmethod == False:
        image = _get_image(i)
        return pygame.mask.from_surface(image)
    else:
        return i.mask


def _get_image(i):
    if i.image is None or i._staticmethod == False:
        image = i.sculpt_list[i.sculpt_number]
        width, high = image.get_size()
        image = pygame.transform.scale(
            image,
            (i.scale * i.width_scale * width, i.scale * i.high_scale * high)
        )
        image = pygame.transform.rotate(image, i.facing_angle)
        image = pygame.transform.flip(image, i.flip_x, i.flip_y)
        image.set_alpha(255 - i.alpha * 2.55)
        if i._staticmethod == True:
            i.image = image
        return image
    else:
        return i.image


class display:
    """窗口管理类，负责游戏窗口的初始化、刷新、标题设置、事件处理等核心窗口操作"""

    @staticmethod
    def set_window(size=(800, 600), title="GameX!"):
        """
        初始化Pygame环境并创建游戏窗口，必须在游戏启动时首先调用

        :param size: 窗口尺寸，元组形式(width, height)，默认值为(800, 600)
        :type size: tuple[int, int]
        :param title: 窗口标题文字，默认值为"GameX!"
        :type title: str
        :return: 无返回值，通过修改全局变量screen和clock完成初始化
        """
        pygame.init()  # 初始化Pygame所有模块
        global screen, clock
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ic = pygame.image.load(os.path.join(BASE_DIR, "data/images/gameX_icon.jpg"))
        pygame.display.set_icon(ic)
        screen = pygame.display.set_mode(size)  # 创建指定尺寸的窗口表面
        clock = pygame.time.Clock()  # 初始化时钟对象，用于控制帧率
        pygame.display.set_caption(title)  # 设置窗口标题

    @staticmethod
    def set_title(title):
        """
        修改当前游戏窗口的标题

        :param title: 新的窗口标题字符串
        :type title: str
        :return: 无返回值
        """
        pygame.display.set_caption(title)

    @staticmethod
    def set_icon(img):
        ic = pygame.image.load(img)
        pygame.display.set_icon(ic)

    @staticmethod
    def fill(rgb: tuple = (255, 255, 255)):
        """
        用指定RGB颜色填充整个屏幕（用于清除上一帧画面）

        :param rgb: RGB颜色元组，格式为(red, green, blue)，每个值范围0-255，默认白色(255,255,255)
        :type rgb: tuple[int, int, int]
        :return: 无返回值
        """
        screen.fill(rgb)

    @staticmethod
    def enable_exit():
        """
        检测窗口关闭事件（用户点击右上角关闭按钮），触发时退出程序

        :return: 无返回值，若检测到QUIT事件则调用sys.exit()终止程序
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()  # 退出程序

    @staticmethod
    def update():
        """
        刷新屏幕，按role_list中的顺序渲染所有可见角色和绘图对象
        渲染规则：列表中靠前的元素层级更低（可能被后面的元素覆盖）

        :return: 无返回值，完成所有对象绘制后更新屏幕显示
        """

        # 遍历所有角色/绘图对象并渲染

        # 使用map进行批量绘制
        list(map(_draw_role, role_list))
        list(map(_draw_pen, role_list))
        pygame.display.flip()

    @staticmethod
    def tick(fps):
        """
        控制游戏帧率，确保游戏运行速度稳定

        :param fps: 每秒刷新次数（帧率），例如60表示每秒60帧
        :type fps: int
        :return: 无返回值，通过时钟控制每帧的停留时间
        """
        global clock
        clock.tick(fps)


class position:
    """坐标处理类，采用以屏幕中心为原点的相对坐标系统，简化角色位置计算"""

    def __init__(self, x, y):
        """
        初始化坐标对象，存储基于屏幕中心的相对坐标

        :param x: 相对于屏幕中心的X坐标（向右为正，向左为负）
        :type x: int或float
        :param y: 相对于屏幕中心的Y坐标（向上为正，向下为负）
        :type y: int或float
        """
        self.x = x  # 相对X坐标
        self.y = y  # 相对Y坐标

    @property
    def real_x(self):
        """
        转换为屏幕绝对X坐标（屏幕左上角为原点，向右为正）

        :return: 绝对X坐标值
        :rtype: float
        """
        return screen.get_size()[0] * 0.5 + self.x  # 屏幕宽度的一半 + 相对X坐标

    @property
    def real_y(self):
        """
        转换为屏幕绝对Y坐标（屏幕左上角为原点，向下为正）

        :return: 绝对Y坐标值
        :rtype: float
        """
        return screen.get_size()[1] * 0.5 - self.y  # 屏幕高度的一半 - 相对Y坐标（因相对坐标向上为正）


class role(pygame.sprite.Sprite):
    """游戏角色类，支持角色移动、造型切换、碰撞检测、图层调整等核心功能"""

    def __init__(self, _staticmethod=False):
        super().__init__()
        self.position = position(0, 0)  # 角色坐标（基于position类的相对坐标）
        self.sculpt_list = list()  # 角色造型列表（存储Pygame图像对象，支持多造型切换）
        self.sculpt_number = None  # 当前使用的造型索引（None表示未设置造型）
        self.scale = 1  # 整体缩放比例（1表示原始大小，>1放大，<1缩小）
        self.width_scale = 1  # 宽度单独缩放比例（与scale相乘，用于非均匀缩放）
        self.high_scale = 1  # 高度单独缩放比例（与scale相乘，用于非均匀缩放）
        self.facing_angle = 0  # 面向角度（单位：度，0为向右，逆时针旋转角度递增）
        self.show = True  # 是否显示角色（False时不参与渲染）
        self.flip_x = False  # 左右翻转开关（True时水平翻转图像，不改变面向角度）
        self.flip_y = False  # 上下翻转开关（True时垂直翻转图像，不改变面向角度）
        self.mask = None  # 碰撞掩码（用于精确碰撞检测，由图像透明度生成）
        self.alpha = 0  # 透明度（0为完全不透明，100为完全透明）
        self.image = None
        self._staticmethod = _staticmethod

        role_list.append(self)  # 将角色添加到全局列表，参与渲染

    def goto(self,x,y):
        self.position.x = x
        self.position.y = y

    def add_sculpt(self, *sculpt_path_list):
        """
        向角色添加造型图像（仅支持gif格式），造型会按添加顺序存入sculpt_list

        :param sculpt_path_list: 一个或多个造型文件的路径（字符串）
        :type sculpt_path_list: str
        :raises FileFindError: 当文件路径不存在时触发
        :raises FileFormatError: 当文件格式不是gif时触发
        :return: 无返回值
        """
        for path in sculpt_path_list:
            # 检查文件是否存在
            if not os.path.exists(path):
                raise f"FileFindError: Can not find file '{path}'"
            # 检查文件格式是否为gif
            file_ext = os.path.splitext(os.path.basename(path))[1].lower()
            if file_ext != '.gif':
                raise "FileFormatError: Only 'gif' format is supported for sculpts"
            # 加载图像并添加到造型列表
            self.sculpt_list.append(pygame.image.load(path))
        # 若未设置当前造型，默认使用第一个添加的造型
        if self.sculpt_number is None and self.sculpt_list:
            self.sculpt_number = 0

    def next_sculpt(self, number=1):
        """
        切换角色造型（循环切换），正数向后切换，负数向前切换

        :param number: 切换次数（例如：1切换到下一个，-1切换到上一个）
        :type number: int
        :raises SculptError: 当角色未添加任何造型（sculpt_list为空）时触发
        :return: 无返回值
        """
        if not self.sculpt_list:
            raise "SculptError: Role has no sculpts (add sculpts first)"
        # 计算新造型索引（取模确保在列表范围内循环）
        self.sculpt_number = (self.sculpt_number + number) % len(self.sculpt_list)

    def forward(self, number: int):
        """
        沿角色当前面向角度移动指定距离

        :param number: 移动距离（正数向前，负数向后）
        :type number: int或float
        :return: 无返回值，直接修改角色position的x和y坐标
        """
        # 将角度转换为弧度（math.cos/sin需要弧度参数）
        radians = math.radians(self.facing_angle)
        # 计算X和Y方向的位移（基于三角函数）
        x_delta = number * math.cos(radians)  # X方向位移（cos控制水平方向）
        y_delta = number * math.sin(radians)  # Y方向位移（sin控制垂直方向）
        # 更新角色位置
        self.position.x += x_delta
        self.position.y += y_delta

    def left_right_flip(self):
        """
        切换角色左右翻转状态（True <-> False），仅影响图像显示，不改变面向角度

        :return: 无返回值
        """
        self.flip_x = not self.flip_x  # 取反当前状态

    def up_down_flip(self):
        """
        切换角色上下翻转状态（True <-> False），仅影响图像显示，不改变面向角度

        :return: 无返回值
        """
        self.flip_y = not self.flip_y  # 取反当前状态

    def adjust_layer(self, mode: str):
        """
        调整角色在渲染层级中的位置（影响遮挡关系）

        :param mode: 调整模式：
            'up'：上移一层（向列表后方移动，层级提高）
            'down'：下移一层（向列表前方移动，层级降低）
            'top'：移至顶层（列表末尾，层级最高）
            'bottom'：移至背景层上方（列表索引1的位置）
        :type mode: str
        :raises TypeError: 当角色位于背景层（索引0）时尝试移动触发
        :raises ValueError: 当mode不是指定的四种模式时触发
        :return: 无返回值
        """
        # 获取当前角色在role_list中的索引（层级）
        current_index = role_list.index(self)

        # 背景层（索引0）不能移动
        if current_index == 0:
            raise TypeError("Background role (layer 0) cannot adjust layer")

        # 根据模式调整层级
        if mode == 'up':
            # 上移一层（若已在顶层则不操作）
            if current_index < len(role_list) - 1:
                # 交换当前角色与下一个角色的位置
                role_list[current_index], role_list[current_index + 1] = role_list[current_index + 1], role_list[
                    current_index]
        elif mode == 'down':
            # 下移一层（若已在背景层上方则不操作）
            if current_index > 1:
                # 交换当前角色与上一个角色的位置
                role_list[current_index], role_list[current_index - 1] = role_list[current_index - 1], role_list[
                    current_index]
        elif mode == 'top':
            # 移至顶层（删除后添加到列表末尾）
            role_list.pop(current_index)
            role_list.append(self)
        elif mode == 'bottom':
            # 移至背景层上方（删除后插入到索引1的位置）
            role_list.pop(current_index)
            role_list.insert(1, self)
        else:
            raise ValueError("mode must be one of ['up', 'down', 'top', 'bottom']")

    def collide(self, target):
        """
        检测当前角色与目标对象是否发生碰撞（基于图像掩码的精确碰撞）

        :param target: 碰撞检测的目标，可以是单个角色(role)或角色组(pygame.sprite.Group)
        :type target: role或pygame.sprite.Group
        :raises ValueError: 当目标类型既不是role也不是Group时触发
        :return: 若碰撞返回目标对象（单个角色或组中碰撞的角色），否则返回False
        :rtype: role或bool
        """
        # 生成当前角色的碰撞掩码（基于处理后的图像）
        image = _get_image(self)
        self.mask = _get_mask(self)
        width, high = image.get_size()
        self_x, self_y = self.position.real_x - width * 0.5, self.position.real_y - high * 0.5

        if isinstance(target, role):
            image = _get_image(target)
            # 目标是单个角色：生成其掩码并检测重叠
            target.mask = pygame.mask.from_surface(image)
            width, high = image.get_size()
            target_x, target_y = target.position.real_x - width * 0.5, target.position.real_y - high * 0.5
            # 计算目标相对于当前角色的坐标偏移
            x_offset = int(target_x - self_x)
            y_offset = int(target_y - self_y)
            # 检测掩码是否重叠（overlap返回重叠点坐标，非None则碰撞）
            if self.mask.overlap(target.mask, (x_offset, y_offset)):
                return target
            return False
        elif isinstance(target, pygame.sprite.Group):
            # 目标是角色组：遍历组中所有角色检测碰撞
            for sprite in target:
                image = _get_image(sprite)
                # 目标是单个角色：生成其掩码并检测重叠
                sprite.mask = _get_mask(sprite)
                width, high = image.get_size()
                sprite_x, sprite_y = sprite.position.real_x - width * 0.5, sprite.position.real_y - high * 0.5
                # 计算目标相对于当前角色的坐标偏移
                x_offset = int(sprite_x - self_x)
                y_offset = int(sprite_y - self_y)
                if self.mask.overlap(sprite.mask, (x_offset, y_offset)):
                    return sprite
            return False
        else:
            raise ValueError("Target must be a 'role' instance or 'pygame.sprite.Group'")

    def died(self):
        """
        从游戏中移除角色（不再参与渲染和交互）

        :return: 无返回值，从全局列表和所有角色组中删除
        """
        # 若角色属于pygame的精灵组，从组中移除
        if hasattr(self, 'groups'):
            self.kill()  # pygame精灵的内置方法，从所有组中删除
        # 从全局渲染列表中移除
        if self in role_list:
            role_list.remove(self)

    def rotate(self, center_position: tuple[int, int], angle_degrees):
        """
        绕指定中心点旋转角色（改变角色位置，不改变面向角度）

        :param center_position: 旋转中心点的相对坐标（基于屏幕中心）
        :type center_position: tuple[int, int]
        :param angle_degrees: 旋转角度（单位：度，逆时针为正，顺时针为负）
        :type angle_degrees: int或float
        :return: 无返回值，直接修改角色的position坐标
        """
        # 将角度转换为弧度
        theta = math.radians(angle_degrees)
        # 计算中心点的屏幕绝对坐标（相对坐标 -> 绝对坐标）
        screen_width, screen_height = screen.get_size()
        center_x = center_position[0] + screen_width * 0.5  # 中心点绝对X
        center_y = screen_height * 0.5 - center_position[1]  # 中心点绝对Y（相对Y向上为正）

        # 旋转公式：计算旋转后的绝对坐标
        # 公式推导：x' = cx + (x - cx)*cosθ - (y - cy)*sinθ
        #          y' = cy + (x - cx)*sinθ + (y - cy)*cosθ
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        # 当前角色的绝对坐标
        current_x = self.position.real_x
        current_y = self.position.real_y
        # 计算旋转后的绝对坐标
        new_x = center_x + (current_x - center_x) * cos_theta - (current_y - center_y) * sin_theta
        new_y = center_y + (current_x - center_x) * sin_theta + (current_y - center_y) * cos_theta
        # 将新绝对坐标转换回相对坐标并更新角色位置
        self.position.x = new_x - screen_width * 0.5
        self.position.y = screen_height * 0.5 - new_y

    @staticmethod
    def new_group():
        """
        创建一个新的角色组（用于批量管理角色，如碰撞检测、统一移动等）

        :return: 新的pygame精灵组对象
        :rtype: pygame.sprite.Group
        """
        return pygame.sprite.Group()


class mouse:
    """鼠标交互类，提供鼠标位置、点击检测、与角色碰撞检测等功能"""

    def collide(self, role: role):
        """
        检测鼠标指针是否与指定角色发生碰撞（基于角色图像的透明区域）

        :param role: 目标角色对象
        :type role: role
        :return: 若碰撞返回True，否则返回False
        :rtype: bool
        """
        # 获取角色处理后的图像及尺寸
        image = _get_image(role)
        role.mask = pygame.mask.from_surface(image)
        width, height = image.get_size()
        # 计算角色图像在屏幕上的绘制区域（左上角坐标）
        role_x = role.position.real_x - width * 0.5  # 图像左上角X
        role_y = role.position.real_y - height * 0.5  # 图像左上角Y
        # 获取当前鼠标位置（绝对坐标）
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # 先快速检测鼠标是否在角色图像的矩形范围内（优化性能）
        if not (role_x <= mouse_x <= role_x + width and role_y <= mouse_y <= role_y + height):
            return False
        # 再通过掩码检测鼠标是否在角色的非透明区域（精确碰撞）
        # 计算鼠标相对于图像左上角的坐标
        relative_x = int(mouse_x - role_x)
        relative_y = int(mouse_y - role_y)
        # 检测该位置是否为非透明像素（掩码中1表示非透明）
        return role.mask.get_at((relative_x, relative_y)) == 1

    def click(self, which):
        """
        检测指定鼠标按键是否被按下（持续检测，按下期间一直返回True）

        :param which: 按键标识：0或"left"（左键）、1或"middle"（中键）、2或"right"（右键）
        :type which: int或str
        :raises ValueError: 当按键标识无效时触发
        :return: 按键按下返回True，否则返回False
        :rtype: bool
        """
        # 映射按键标识到索引（0=左键，1=中键，2=右键）
        if which in (0, "left"):
            index = 0
        elif which in (1, "middle"):
            index = 1
        elif which in (2, "right"):
            index = 2
        else:
            raise ValueError("which must be 0/left, 1/middle, or 2/right")
        # 获取鼠标按键状态（元组：(左键状态, 中键状态, 右键状态)，True为按下）
        return pygame.mouse.get_pressed()[index]

    @property
    def x(self):
        """
        获取鼠标指针的X坐标（基于屏幕中心的相对坐标，向右为正）
        """
        # 绝对X坐标 - 屏幕宽度的一半 = 相对X坐标
        return pygame.mouse.get_pos()[0] - screen.get_size()[0] * 0.5

    @property
    def y(self):
        """
        获取鼠标指针的Y坐标（基于屏幕中心的相对坐标，向上为正）
        """
        # 屏幕高度的一半 - 绝对Y坐标 = 相对Y坐标（因绝对坐标向下为正）
        return screen.get_size()[1] * 0.5 - pygame.mouse.get_pos()[1]


class key:
    """键盘交互类，提供按键按下状态的检测功能"""

    @staticmethod
    def press(Key):
        """
        检测指定键盘按键是否被按下（持续检测，按下期间一直返回True）
        :param Key: 按键名称（字符串），支持Pygame所有按键常量对应的名称，如"a"、"esc"、"up"等
        :type Key: str
        :return: 按键按下返回True，否则返回False
        :rtype: bool
        """
        # 特殊处理"esc"（对应Pygame的K_ESCAPE）
        if Key.lower() == "esc":
            key_code = pygame.K_ESCAPE
        else:
            # 将按键名称转换为Pygame的按键编码
            key_code = pygame.key.key_code(Key.lower())
        # 获取所有按键的状态（元组，索引为按键编码，值为bool）
        return pygame.key.get_pressed()[key_code]


class sound:
    """音频管理类，支持音频加载、播放、音量控制、通道管理等功能"""

    def __init__(self):
        """初始化音频混合器，创建音频存储字典（名称->Sound对象）"""
        pygame.mixer.init()  # 初始化Pygame音频系统
        self.music_dict = dict()  # 存储加载的音频：{名称: pygame.mixer.Sound对象}

    def load_sound(self, sound_name, sound_path):
        """
        加载音频文件并指定名称（用于后续播放控制），支持mp3和wav格式
        :param sound_name: 音频名称（自定义，用于标识该音频）
        :type sound_name: str或int
        :param sound_path: 音频文件路径（绝对路径或相对路径）
        :type sound_path: str
        :raises FileFindError: 当文件路径不存在时触发
        :raises FileFormatError: 当文件格式不是mp3或wav时触发
        :return: 无返回值
        """
        # 检查文件是否存在
        if not os.path.exists(sound_path):
            raise f"FileFindError: Can not find audio file '{sound_path}'"
        # 检查文件格式是否为mp3或wav
        file_ext = os.path.splitext(os.path.basename(sound_path))[1].lower()
        if file_ext not in ('.mp3', '.wav'):
            raise "FileFormatError: Only 'mp3' and 'wav' formats are supported"
        # 加载音频并存储到字典
        self.music_dict[sound_name] = pygame.mixer.Sound(sound_path)

    def play_sound(self, sound_name, channel=None, loops=1):
        """
        播放指定名称的音频
        :param sound_name: 加载时指定的音频名称
        :type sound_name: str或int
        :param channel: 播放通道（整数，默认使用当前可用通道），范围取决于set_channel的设置
        :type channel: int或None
        :param loops: 循环次数（-1表示无限循环，1表示播放1次，2表示播放2次等）
        :type loops: int
        :return: 无返回值
        """
        # 获取音频对象
        sound_obj = self.music_dict.get(sound_name)
        if not sound_obj:
            raise ValueError(f"Sound '{sound_name}' not loaded (call load_sound first)")
        # 播放音频（指定通道或默认通道）
        if channel is None:
            sound_obj.play(loops=loops - 1)  # pygame的loops参数：0=1次，1=2次，故减1
        else:
            # 通过指定通道播放（需确保通道存在）
            pygame.mixer.Channel(channel).play(sound_obj, loops=loops - 1)

    def set_channel(self, number: int):
        """
        设置音频播放通道的数量（默认8个通道），通道用于同时播放多个音频

        :param number: 通道数量（正整数）
        :type number: int
        :return: 无返回值
        """
        pygame.mixer.set_num_channels(number)

    def set_volume(self, sound_name, volume):
        """
        设置指定音频的音量（0.0-1.0，0为静音，1.0为最大音量）

        :param sound_name: 音频名称（加载时指定）
        :type sound_name: str或int
        :param volume: 音量值（范围0.0-1.0）
        :type volume: float
        :return: 无返回值
        """
        sound_obj = self.music_dict.get(sound_name)
        if not sound_obj:
            raise ValueError(f"Sound '{sound_name}' not loaded")
        sound_obj.set_volume(volume)

    def stop_sound(self, sound_name):
        """
        立即停止指定音频的播放

        :param sound_name: 音频名称（加载时指定）
        :type sound_name: str或int
        :return: 无返回值
        """
        sound_obj = self.music_dict.get(sound_name)
        if sound_obj:
            sound_obj.stop()

    def stop(self):
        """停止所有正在播放的音频（所有通道）"""
        pygame.mixer.stop()

    def fadeout(self, sound_name, time: int):
        """
        平滑停止指定音频（音量逐渐减小至0）

        :param sound_name: 音频名称（加载时指定）
        :type sound_name: str或int
        :param time: 淡出时间（单位：毫秒，例如1000表示1秒内淡出）
        :type time: int
        :return: 无返回值
        """
        sound_obj = self.music_dict.get(sound_name)
        if not sound_obj:
            raise ValueError(f"Sound '{sound_name}' not loaded")
        sound_obj.fadeout(time)


class pen:
    """绘图工具类，用于在屏幕上绘制直线、矩形等图形，支持颜色设置和图层调整"""

    def __init__(self, width=None, high=None):
        # 若未指定尺寸，使用屏幕尺寸
        if width is None or high is None:
            width, high = screen.get_size()
        # 创建透明表面（支持alpha通道，初始全透明）
        self.layer = pygame.Surface((width, high), pygame.SRCALPHA)
        self.layer.fill((0, 0, 0, 0))  # 填充全透明（RGBA：最后一位为alpha）
        self.color = (0, 0, 0)  # 默认绘图颜色为黑色（RGB元组）
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.font = os.path.join(BASE_DIR, "data/fonts/My_font.ttf")
        role_list.append(self)  # 添加到全局列表，参与渲染

    def set_font(self, font_path):
        self.font = font_path  # 默认字体

    def line(self, start: tuple[int, int], end: tuple[int, int], size=2):
        # 将相对坐标转换为屏幕绝对坐标
        screen_width, screen_height = screen.get_size()
        start_x = start[0] + screen_width * 0.5  # 起点绝对X
        start_y = screen_height * 0.5 - start[1]  # 起点绝对Y
        end_x = end[0] + screen_width * 0.5  # 终点绝对X
        end_y = screen_height * 0.5 - end[1]  # 终点绝对Y
        # 绘制普通直线 (line)
        pygame.draw.line(self.layer, self.color, (start_x, start_y), (end_x, end_y), size)

    def aaline(self, start: tuple[int, int], end: tuple[int, int]):
        # 将相对坐标转换为屏幕绝对坐标
        screen_width, screen_height = screen.get_size()
        start_x = start[0] + screen_width * 0.5  # 起点绝对X
        start_y = screen_height * 0.5 - start[1]  # 起点绝对Y
        end_x = end[0] + screen_width * 0.5  # 终点绝对X
        end_y = screen_height * 0.5 - end[1]  # 终点绝对Y
        # 绘制抗锯齿直线（aaline）
        pygame.draw.aaline(self.layer, self.color, (start_x, start_y), (end_x, end_y))

    def rect(self, top_left: tuple[int, int], width, high):
        # 转换左上角相对坐标为绝对坐标
        screen_width, screen_height = screen.get_size()
        x = top_left[0] + screen_width * 0.5
        y = screen_height * 0.5 - top_left[1]
        # 绘制矩形（Rect对象：(x, y, width, height)）
        pygame.draw.rect(self.layer, self.color, (x, y, width, high))

    def write(self, text, pos: tuple[int, int], size):
        # 将相对坐标转换为屏幕绝对坐标
        screen_width, screen_height = screen.get_size()
        center_x = pos[0] + screen_width * 0.5  # 文本中心的绝对X坐标
        center_y = screen_height * 0.5 - pos[1]  # 文本中心的绝对Y坐标

        # 创建字体并渲染文本
        font = pygame.font.Font(self.font, size)  # 支持中文
        text_surface = font.render(text, True, self.color)

        # 获取文本矩形并设置其中心点
        text_rect = text_surface.get_rect()
        text_rect.center = (center_x, center_y)  # 将文本中心与计算的坐标对齐

        # 绘制文本
        self.layer.blit(text_surface, text_rect)

    def set_color(self, rgb: tuple = (0, 0, 0)):
        self.color = rgb

    def adjust_layer(self, mode: str):
        current_index = role_list.index(self)

        if current_index == 0:
            raise TypeError("Background layer (index 0) cannot adjust layer")

        if mode == 'up':
            if current_index < len(role_list) - 1:
                role_list[current_index], role_list[current_index + 1] = role_list[current_index + 1], role_list[
                    current_index]
        elif mode == 'down':
            if current_index > 1:
                role_list[current_index], role_list[current_index - 1] = role_list[current_index - 1], role_list[
                    current_index]
        elif mode == 'top':
            role_list.pop(current_index)
            role_list.append(self)
        elif mode == 'bottom':
            role_list.pop(current_index)
            role_list.insert(1, self)
        else:
            raise ValueError("mode must be one of ['up', 'down', 'top', 'bottom']")

    def died(self):
        """从游戏中移除绘图层（不再参与渲染）"""
        if self in role_list:
            role_list.remove(self)

    def clear(self):
        self.layer.fill((0, 0, 0, 0))  # 填充全透明（RGBA：最后一位为alpha）


class color:
    """预设颜色类，提供常用颜色的RGB值，便于直接调用"""

    def __init__(self):
        self.red = (255, 0, 0)  # 红色
        self.orange = (255, 165, 0)  # 橙色
        self.yellow = (255, 255, 0)  # 黄色
        self.green = (0, 255, 0)  # 绿色
        self.blue = (0, 0, 255)  # 蓝色
        self.cyan = (0, 255, 255)  # 青色
        self.white = (255, 255, 255)  # 白色
        self.black = (0, 0, 0)  # 黑色


# 全局背景角色（初始加入role_list，索引0，作为最底层）
background = role()
# 全局颜色对象（可直接调用预设颜色）
color = color()
mouse = mouse()


def help(cont=None):
    """
    输出各模块的帮助文档，说明类和方法的使用方式

    :param cont: 要查询的模块名称，可选值：'all'（所有模块）、'display'、'background'、'mouse'、
                 'sound'、'pen'、'key'、'role'；None时触发ValueError
    :type cont: str或None
    :raises ValueError: 当cont不是指定值时触发
    """
    __display__ = \
        '''
    -------------------display模块-------------------
    窗口管理核心模块，负责游戏窗口的初始化、刷新、事件处理等。

    方法说明：
    - update():
        刷新屏幕，按role_list顺序渲染所有可见角色和绘图对象（靠前元素层级低）。

    - set_window(size=(800, 600), title="GameX!"):
        初始化Pygame和游戏窗口。
        参数：
            size: 窗口尺寸元组(width, height)，默认(800, 600)
            title: 窗口标题字符串，默认"GameX!"

    - set_title(str):
        修改窗口标题。
        参数：str为新标题内容。
    
    - set_icon(img):
        涉足窗口图标
        参数：img文件(支持ico、jpg、png)

    - fill(rgb=(255, 255, 255)):
        用指定颜色填充屏幕（清除上一帧）。
        参数：rgb为颜色元组(red, green, blue)，默认白色。

    - enable_exit():
        检测窗口关闭事件（用户点击关闭按钮），触发时退出程序。

    - tick(FPS):
        控制游戏帧率（每秒刷新次数）。
        参数：FPS为整数（如60表示每秒60帧）。
    '''

    __background__ = \
        '''
    -------------------background模块-------------------
    全局背景角色，初始位于role_list的索引0（最底层），可作为游戏背景使用。
    继承role类的所有方法，可添加背景图像、调整显示状态等。

    示例：
        background.add_sculpt("bg.gif")  # 为背景添加图像
        background.show = True           # 显示背景（默认True）
    '''

    __mouse__ = \
        '''
    -------------------mouse模块-------------------
    鼠标交互模块，提供鼠标位置、点击检测、与角色碰撞检测功能。

    方法说明：
    - collide(role):
        检测鼠标是否与指定角色碰撞（基于角色图像的非透明区域）。
        参数：role为目标角色对象。
        返回：碰撞返回True，否则False。

    - click(which):
        检测指定鼠标按键是否被按下。
        参数：which为按键标识（0/left=左键，1/middle=中键，2/right=右键）。
        返回：按下返回True，否则False。

    属性：
    - x: 鼠标X坐标（基于屏幕中心的相对坐标，右为正）。
    - y: 鼠标Y坐标（基于屏幕中心的相对坐标，上为正）。
    '''

    __sound__ = \
        '''
    -------------------sound模块-------------------
    音频管理模块，支持音频加载、播放、音量控制等。

    方法说明：
    - load_sound(sound_name, sound_path):
        加载音频文件并命名，支持mp3和wav格式。
        参数：
            sound_name: 自定义音频名称（用于后续操作）
            sound_path: 音频文件路径（绝对或相对路径）
        异常：文件不存在触发FileFindError；格式错误触发FileFormatError。

    - play_sound(sound_name, channel=None, loops=1):
        播放指定音频。
        参数：
            sound_name: 加载时指定的音频名称
            channel: 播放通道（整数，默认使用可用通道）
            loops: 循环次数（1=播放1次，-1=无限循环）

    - fadeout(sound_name, time):
        平滑停止音频（音量逐渐减小至0）。
        参数：
            sound_name: 音频名称
            time: 淡出时间（毫秒）

    - stop():
        立即停止所有正在播放的音频。

    - stop_sound(sound_name):
        立即停止指定音频。
        参数：sound_name为音频名称。

    - set_volume(sound_name, volume):
        设置音频音量。
        参数：
            sound_name: 音频名称
            volume: 音量值（0.0-1.0，0为静音）

    - set_channel(number):
        设置音频播放通道数量（默认8个）。
        参数：number为通道数量（正整数）。
    '''

    __pen__ = \
        '''
    -------------------pen模块-------------------
    绘图工具模块，用于在屏幕上绘制直线、矩形等图形，支持颜色设置和图层调整。

    方法说明：
    - line(start, end, size):
        绘制直线。
        参数：
            start: 起点相对坐标(x, y)（基于屏幕中心）
            end: 终点相对坐标(x, y)（基于屏幕中心）
            size: 画笔粗细
            
    - aaline(start, end):
        绘制抗锯齿直线。
        参数：
            start: 起点相对坐标(x, y)（基于屏幕中心）
            end: 终点相对坐标(x, y)（基于屏幕中心）


    - set_color(rgb=(0, 0, 0)):
        设置绘图颜色。
        参数：rgb为颜色元组(red, green, blue)，默认黑色。
        示例：pen.set_color(color.red)  # 使用预设红色
        
    - write(text, pos, size):
        在窗口中书写。
        参数:
            text：书写内容
            pos：书写位置
            size：字的大小
            
    - set_font(font_path):
        设置字体。
        参数：font设置字体

    - draw_rect(top_left, width, high):
        绘制矩形。
        参数：
            top_left: 左上角相对坐标(x, y)
            width: 矩形宽度（像素）
            high: 矩形高度（像素）

    - adjust_layer(mode):
        调整绘图层在渲染层级中的位置。
        参数：mode为调整模式（'up'上移一层，'down'下移一层，'top'移至顶层，'bottom'移至背景上）。
        异常：背景层（索引0）移动时触发TypeError。
    '''

    __key__ = \
        '''
    -------------------key模块-------------------
    键盘交互模块，用于检测键盘按键的按下状态。

    方法说明：
    - press(Key):
        检测指定按键是否被按下（持续检测）。
        参数：Key为按键名称字符串（如"a"、"esc"、"up"）。
        返回：按下返回True，否则False。

    示例：
        if key.press("space"):  # 检测空格键是否按下
            print("Space pressed!")
    '''

    __role__ = \
        '''
    -------------------role模块-------------------
    游戏角色核心模块，支持角色移动、造型切换、碰撞检测等功能。

    属性说明：
    - position: 角色坐标（position对象，含x/y相对坐标和real_x/real_y绝对坐标）
    - sculpt_number: 当前造型索引（从0开始）
    - scale: 整体缩放比例（1为原始大小）
    - show: 是否显示角色（bool，False时不渲染）
    - width_scale/high_scale: 宽/高单独缩放比例（与scale相乘）
    - facing_angle: 面向角度（度，0向右，逆时针递增）
    - alpha: 透明度（0不透明，100完全透明）

    方法说明：
    - add_sculpt(*sculpt_path_list):
        向角色添加造型（仅支持gif）。
        参数：一个或多个造型文件路径（字符串）。
        异常：文件不存在触发FileFindError；格式非gif触发FileFormatError。

    - next_sculpt(number=1):
        切换造型（循环切换）。
        参数：number为切换次数（正数向后，负数向前）。
        异常：无造型时触发SculptError。

    - forward(number):
        沿面向角度移动指定距离。
        参数：number为距离（正数向前，负数向后）。

    - left_right_flip():
        切换左右翻转状态（不改变面向角度）。

    - up_down_flip():
        切换上下翻转状态（不改变面向角度）。

    - adjust_layer(mode):
        调整角色渲染层级（同pen模块）。
        异常：背景角色（索引0）移动触发TypeError。

    - collide(other):
        检测与目标的碰撞（精确碰撞）。
        参数：other为角色(role)或角色组(Group)。
        返回：碰撞返回目标对象，否则False。

    - died():
        从游戏中移除角色（从role_list和所有组中删除）。

    - new_group():
        创建角色组（用于批量管理角色）。
        返回：pygame.sprite.Group对象。

    - rotate(center_position, angle_degrees):
        绕指定中心点旋转角色。
        参数：
            center_position: 中心点相对坐标(x, y)
            angle_degrees: 旋转角度（度，逆时针为正）
    '''

    # 根据参数输出对应帮助文档
    if cont == 'all':
        print(__display__)
        print(__background__)
        print(__mouse__)
        print(__sound__)
        print(__pen__)
        print(__key__)
        print(__role__)
    elif cont == 'display':
        print(__display__)
    elif cont == 'background':
        print(__background__)
    elif cont == 'mouse':
        print(__mouse__)
    elif cont == 'sound':
        print(__sound__)
    elif cont == 'pen':
        print(__pen__)
    elif cont == 'key':
        print(__key__)
    elif cont == 'role':
        print(__role__)
    else:
        raise ValueError("cont must be one of: 'all', 'display', 'background', 'mouse', 'sound', 'pen', 'key', 'role'")
