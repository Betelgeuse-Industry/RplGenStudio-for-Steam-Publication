#!/usr/bin/env python
# coding: utf-8

# 图形界面的主界面

import os
import sys
import tkinter as tk
import ttkbootstrap as ttk
from pathlib import Path
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.dialogs import Messagebox, MessageCatalog
from PIL import Image, ImageTk

from .ProjConfig import Preference, preference
from .GUI_Link import Link
from .Utils import EDITION
# 项目视图
from .GUI_View import EmptyView, ProjectView, ConsoleView, ScriptView, PreferenceView

class RplGenStudioMainWindow(ttk.Window):
    def __init__(
            self
            )->None:
        # 系统缩放比例
        self.sz = self.get_screenzoom()
        super().__init__(
            title       = f'回声工坊 {EDITION}',
            iconphoto   = './media/icon.png',
            size        = (int(1500*self.sz),int(800*self.sz)),
            resizable   = (True,True),
        )
        # home
        self.home_dir = Path(os.path.expanduser("~"))
        self.load_recent_project()
        # 关闭
        self.protocol('WM_DELETE_WINDOW',self.on_close)
        # 主题配置
        self.theme_config(preference.theme)
        # 标题
        self.window_title = f'回声工坊 {EDITION}'
        # 导航栏
        self.show = 'project'
        self.navigate_bar = NavigateBar(master=self,screenzoom=self.sz)
        self.navigate_bar.place(x=0,y=0,width=int(80*self.sz),relheight=1)
        # event
        self.navigate_bar.bind('<ButtonRelease-1>', self.navigateBar_get_click)
        # self.bind('<F11>', self.switch_fullscreen) # BUG 全屏模式下的窗口上下顺序会出现异常
        # 视图
        self.view = {
            'project': EmptyView(master=self,screenzoom=self.sz),
            'console': ConsoleView(master=self,screenzoom=self.sz),
            'script' : ScriptView( master=self,screenzoom=self.sz),
            'setting': PreferenceView(master=self,screenzoom=self.sz)
        }
        self.view_show('project')
    # 初始化字体
    def font_init(self):
        # 字体
        # 系统字体
        if preference.lang == 'zh':
            if 'win32' in sys.platform:
                system_font_family = '微软雅黑'
            elif 'linux' in sys.platform:
                system_font_family = '文泉驿微米黑'
            elif 'darwin' in sys.platform:
                system_font_family = '华文黑体'
            else:
                system_font_family = '华文黑体'
        else:
            # TODO: 英文
            if 'win32' in sys.platform:
                system_font_family = '微软雅黑'
            elif 'linux' in sys.platform:
                system_font_family = '文泉驿微米黑'
            elif 'darwin' in sys.platform:
                system_font_family = '华文黑体'
            else:
                system_font_family = '华文黑体'
        self.system_font_family = system_font_family
        Link['system_font_family'] = system_font_family
        # 终端字体
        if preference.lang == 'zh':
            try:
                from tkextrafont import Font as FileFont
                self.terminal_font = FileFont(file='./media/sarasa-mono-sc-regular.ttf')
                terminal_font_family = 'Sarasa Mono SC'
            except:
                terminal_font_family = system_font_family
        else:
            try:
                from tkextrafont import Font as FileFont
                self.terminal_font = FileFont(file='./media/sarasa-mono-sc-regular.ttf')
                terminal_font_family = 'Sarasa Mono SC'
            except:
                terminal_font_family = system_font_family
        self.terminal_font_family = terminal_font_family
        Link['terminal_font_family'] = terminal_font_family
    # 初始化主题
    def theme_config(self,theme):
        self.font_init()
        self.style.load_user_themes('./media/GUI_theme.json')
        # 样式
        SZ_5 = int(5 * self.sz)
        text_label_pad = (SZ_5,0,SZ_5,0)
        # 载入主题
        self.style.theme_use(theme)
        # self
        # 使用主题
        if theme == 'rplgenlight':
            self.style.configure('terminal.TButton',compound='left',font=(self.system_font_family, 14, "bold"))
            self.style.configure('output.TButton',compound='left',font=(self.system_font_family, 14, "bold"))
            # bootstyle
            self.style.configure('success.TButton',font=(self.system_font_family, 18, "bold"),anchor='w') # dark
            self.style.configure('info.TButton',font=(self.system_font_family, 16, "bold"),anchor='center',foreground="#555555") # lightgrey
            self.style.configure('light.TButton',anchor='w') # light
            # 媒体定义的颜色标签
            self.style.configure('Violet.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#a690e0')
            self.style.configure('Iris.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#729acc')
            self.style.configure('Caribbean.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#29d698')
            self.style.configure('Lavender.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#e384e3')
            self.style.configure('Cerulean.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#2fbfde')
            self.style.configure('Forest.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#51b858')
            self.style.configure('Rose.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#f76fa4')
            self.style.configure('Mango.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#eda63b')
            self.style.configure('Purple.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#970097')
            self.style.configure('Blue.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#3c3cff')
            self.style.configure('Teal.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#008080')
            self.style.configure('Magenta.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#e732e7')
            self.style.configure('Tan.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#cec195')
            self.style.configure('Green.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#1d7021')
            self.style.configure('Brown.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#8b4513')
            self.style.configure('Yellow.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#e2e264')
            # 角色表的表头样式
            self.style.configure('CharHead.TLabel',anchor='left',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#ffffff',background='#51b858')
            # 显示内容的头文本
            self.style.configure('comment.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#bfbfbf') # 浅灰色
            self.style.configure('dialog.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#0f86cb') # 蓝色的
            self.style.configure('setdync.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#008000') # 绿色的
            self.style.configure('place.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#e60074') # 品红
            self.style.configure('invasterisk.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#cc0000') # 红色的
            # 显示内容的主文本
            self.style.configure('main.TLabel',anchor='w',font=(self.system_font_family, 10),padding=text_label_pad) # 黑色的
            self.style.configure('ingore.TLabel',anchor='w',font=(self.system_font_family, 10),padding=text_label_pad,foreground='#bfbfbf') # 浅灰色
            self.style.configure('method.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#bf8000') # 橙色的
            self.style.configure('digit.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#6600cc') # 紫色的
            self.style.configure('fuction.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#009898') # 蓝色的
            self.style.configure('object.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#303030') # 深灰色
            self.style.configure('exception.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#cc0000') # 红色的
            # 预览窗体
            self.style.configure('preview.TLabel',anchor='center',background='#333333',borderwidth=0)
        elif theme == 'rplgendark':
            # self.dark_title_bar() # 有bug，在win10不正常显示
            self.style.configure('terminal.TButton',compound='left',font=(self.system_font_family, 14, "bold"))
            self.style.configure('output.TButton',compound='left',font=(self.system_font_family, 14, "bold"))
            # bootstyle
            self.style.configure('success.TButton',font=(self.system_font_family, 18, "bold"),anchor='w') # dark
            self.style.configure('info.TButton',font=(self.system_font_family, 16, "bold"),anchor='center',foreground="#aaaaaa") # lightgrey
            self.style.configure('light.TButton',anchor='w') # light
            # 媒体定义的颜色标签
            self.style.configure('Violet.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#a690e0')
            self.style.configure('Iris.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#729acc')
            self.style.configure('Caribbean.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#29d698')
            self.style.configure('Lavender.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#e384e3')
            self.style.configure('Cerulean.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#2fbfde')
            self.style.configure('Forest.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#51b858')
            self.style.configure('Rose.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#f76fa4')
            self.style.configure('Mango.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#eda63b')
            self.style.configure('Purple.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#970097')
            self.style.configure('Blue.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#3c3cff')
            self.style.configure('Teal.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#008080')
            self.style.configure('Magenta.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#e732e7')
            self.style.configure('Tan.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#cec195')
            self.style.configure('Green.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#1d7021')
            self.style.configure('Brown.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#8b4513')
            self.style.configure('Yellow.TLabel',anchor='center',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,background='#1d1d1d',foreground='#e2e264')
            # 角色表的表头样式
            self.style.configure('CharHead.TLabel',anchor='left',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#eeeeee',background='#505050')
            # 显示内容的头文本
            self.style.configure('comment.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#bfbfbf') # 浅灰色
            self.style.configure('dialog.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#c188e9') # 蓝色的
            self.style.configure('setdync.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#008000') # 绿色的
            self.style.configure('place.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#e60074') # 品红
            self.style.configure('invasterisk.TLabel',anchor='w',font=(self.system_font_family, 12, "bold"),padding=text_label_pad,foreground='#cc0000') # 红色的
            # 显示内容的主文本
            self.style.configure('main.TLabel',anchor='w',font=(self.system_font_family, 10),padding=text_label_pad) # 黑色的
            self.style.configure('ingore.TLabel',anchor='w',font=(self.system_font_family, 10),padding=text_label_pad,foreground='#bfbfbf') # 浅灰色
            self.style.configure('method.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#bf8000') # 橙色的
            self.style.configure('digit.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#6600cc') # 紫色的
            self.style.configure('fuction.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#009898') # 蓝色的
            self.style.configure('object.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#303030') # 深灰色
            self.style.configure('exception.TLabel',anchor='w',font=(self.system_font_family, 10, "bold"),padding=text_label_pad,foreground='#cc0000') # 红色的
            # 预览窗体
            self.style.configure('preview.TLabel',anchor='center',background='#333333',borderwidth=0)
    # 当关闭窗口时
    def on_close(self):
        if type(self.view['project']) is EmptyView:
            pass
        elif type(self.view['project']) is ProjectView:
            w = int(self.winfo_width()/2)
            h = int(self.winfo_height()/2-self.sz*100)
            x = int(self.winfo_x())
            y = int(self.winfo_y())
            choice = Messagebox().show_question(
            message='确认要关闭软件？\n尚未保存的项目变更将会丢失！',
            title='警告！',
            buttons=["取消:secondary","确定:danger"],
            alert=True,
            position=(x+w,y+h),
            width=100
            )
            if choice != '确定':
                return False
        self.dump_recent_project()
        self.destroy()
    # 当导航栏被点击时
    def navigateBar_get_click(self,event):
        is_wide = not self.navigate_bar.is_wide
        navigate_bar_width = int({True:180,False:80}[is_wide] * self.sz)
        self.navigate_bar.place_widgets(is_wide)
        self.navigate_bar.place_configure(width=navigate_bar_width)
        self.view[self.show].place_configure(x=navigate_bar_width,width=-navigate_bar_width)
    # 显示指定的视图
    def view_show(self,show:str):
        # 清除原有显示的view
        self.view[self.show].place_forget()
        # 显示新的
        navigate_bar_width = int({True:180,False:80}[self.navigate_bar.is_wide] * self.sz)
        self.view[show].place(x=navigate_bar_width,y=0,relwidth=1,relheight=1,width=-navigate_bar_width)
        self.show = show
    # 获取系统的缩放比例
    def get_screenzoom(self)->float:
        if 'win32' in sys.platform:
            try:
                from ctypes import windll
                return windll.shcore.GetScaleFactorForDevice(0) / 100
            except:
                return 1.0
        elif 'linux' in sys.platform:
            return 1.0
        else:
            print(sys.platform)
            return 2.0
    # 进入或者取消全屏
    def switch_fullscreen(self,event):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))
    # 显示toast
    def show_toast(self,message,title='test'):
        toast = ToastNotification(title=title,message=message)
        toast.show_toast()
        toast.toplevel.lift()
    # 仅适用于windows，深色模式窗口
    def dark_title_bar(self):
        if 'win32' in sys.platform:
            # 使标题栏变黑
            import ctypes
            self.update()
            set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute # 设置窗口属性
            get_parent = ctypes.windll.user32.GetParent # 找父窗口
            hwnd = get_parent(self.winfo_id()) # 获取它的wininfo_id转换成句柄
            rendering_policy = 20 # 设置暗黑模式数值 # DWM渲染模式？
            value = 2
            value = ctypes.c_int(value)
            set_window_attribute(hwnd, rendering_policy, ctypes.byref(value), ctypes.sizeof(value)) # 设置
            self.update() # 更新
    # 载入最近的项目
    def load_recent_project(self):
        path = self.home_dir /'.rplgen' /'recent_project.log'
        try:
            # 从home目录读取
            self.recent_files = open(path,'r',encoding='utf-8').read().split('\n')
        except:
            # 在home目录新建目录
            try:
                os.makedirs(self.home_dir / '.rplgen')
            except FileExistsError:
                pass
            self.recent_files = []
            self.dump_recent_project()
        Link['recent_files'] = self.recent_files
    def dump_recent_project(self):
        try:
            path = self.home_dir /'.rplgen' /'recent_project.log'
            with open(path,'w',encoding='utf-8') as of:
                of.write('\n'.join(self.recent_files))
        except FileNotFoundError:
            pass
# 最右导航栏的
class NavigateBar(ttk.Frame):
    """
    各个元件的尺寸：以100%缩放为准
    -----
    1. 图标的尺寸：50，50
    2. 按钮的尺寸：60，60
    3. 宽版按钮的尺寸：160，60
    4. 按钮和按钮之间的距离：80
    5. 按钮和分割线的距离：80 + 20
    6. 选中标志，在按钮中的尺寸：5，60
    """
    def __init__(self,master,screenzoom) -> None:
        self.sz = screenzoom
        SZ_3 = int(self.sz *3)
        super().__init__(master,borderwidth=10*self.sz,bootstyle='success')
        icon_size = [int(50*self.sz),int(50*self.sz)]
        self.master = master
        self.is_wide = False
        # 图形
        self.image = {
            'logo'      : ImageTk.PhotoImage(name='logo',   image=Image.open('./media/icon.png').resize(icon_size)),
            'setting'   : ImageTk.PhotoImage(name='setting',image=Image.open('./media/icon/setting.png').resize(icon_size)),
            'project'   : ImageTk.PhotoImage(name='project',image=Image.open('./media/icon/project.png').resize(icon_size)),
            'script'    : ImageTk.PhotoImage(name='script', image=Image.open('./media/icon/script.png').resize(icon_size)),
            'console'   : ImageTk.PhotoImage(name='console',image=Image.open('./media/icon/console.png').resize(icon_size)),
        }
        # 顶部
        self.titles = {
            'logo'      : ttk.Button(master=self,image='logo',bootstyle='success',padding=(SZ_3,0,0,0)),
            'set'       : ttk.Button(master=self,image ='setting',text=' 首选项',command=lambda :self.press_button('setting'),bootstyle='success',compound='left',padding=(SZ_3,0,0,0))
        } 
        # 分割线
        self.separator = ttk.Separator(master=self,orient='horizontal',bootstyle='light')
        # 按钮
        self.buttons = {
            'project'   : ttk.Button(master=self,image='project',text=' 项目',command=lambda :self.press_button('project'),bootstyle='success',compound='left',padding=(SZ_3,0,0,0)),
            'script'    : ttk.Button(master=self,image='script',text=' 脚本',command=lambda :self.press_button('script'),bootstyle='success',compound='left',padding=(SZ_3,0,0,0)),
            'console'   : ttk.Button(master=self,image='console',text=' 控制台',command=lambda :self.press_button('console'),bootstyle='success',compound='left',padding=(SZ_3,0,0,0)),
        }
        # 高亮的线
        self.choice = ttk.Frame(master=self,bootstyle='primary')
        # 禁用
        self.disabled = False
        # self.titles
        self.place_widgets(self.is_wide)
        # 置顶
        self.lift()
        self.focus_set()
    # 放置元件
    def place_widgets(self,is_wide:bool):
        self.is_wide = is_wide
        if is_wide:
            width = 160
        else:
            width = 60
        width = int(width*self.sz)
        distance = int(80 * self.sz)
        # self.titles
        for idx,key in enumerate(self.titles.keys()):
            button = self.titles[key]
            if len(button.place_info())==0:
                button.place(width=width,height=width,x=0,y=idx*distance)
            else:
                button.place_configure(width=width)
        # ----------
        if len(self.separator.place_info()) == 0:
            self.separator.place(width=width,x=0,y= (idx+1)*distance)
        else:
            self.separator.place_configure(width=width)
        y_this = idx*distance + int(100 * self.sz)
        # self.buttons
        for idx,key in enumerate(self.buttons.keys()):
            button = self.buttons[key]
            if len(button.place_info())==0:
                button.place(width=width,height=width,x=0, y= y_this + idx*distance)
            else:
                button.place_configure(width=width)
        # 高亮的线
        self.press_button(self.master.show)
    # 点击按键的绑定事件：标注
    def press_button(self,button,force=False):
        # 检查是否禁用
        if self.disabled and force==False:
            ToastNotification(title='禁用图形界面',message='核心程序正在运行中！在核心程序终止前，图形界面已被暂时的禁用。').show_toast()
            return
        position = {'setting':80,'project':180,'script':260,'console':340}[button]*self.sz
        SZ_5 = int(self.sz * 5)
        SZ_60 = int(self.sz * 60)
        if len(self.choice.place_info()) == 0:
            self.choice.place(width=SZ_5,height=SZ_60,x=-SZ_5,y= position)
        else:
            self.choice.place_configure(y=position)
            self.master.view_show(button)
    # 禁用
    def disable_navigate(self):
        self.disabled = True
    def enable_navigate(self):
        self.disabled = False
