#!/usr/bin/env python
# coding: utf-8

# 容器，文件页面的元素之一。
# 包含：可滚动的容器和对应的小节元素

import numpy as np
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.scrolled import ScrolledFrame
import pygame

from .GUI_Util import thumbnail
from .ScriptParser import MediaDef, CharTable, RplGenLog
from .Medias import MediaObj
from .FilePaths import Filepath

# 容纳内容的滚动Frame
class Container(ScrolledFrame):
    def __init__(self,master,content,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master, padding=3, bootstyle='light', autohide=True)
        self.preview_canvas = master.preview
        self.vscroll.config(bootstyle='primary-round')
        self.container.config(bootstyle='light',takefocus=True)
        # 按键绑定
        self.container.bind('<Control-Key-a>',lambda event:self.select_range(event,index=False),"+")
        self.container.bind('<Up>',lambda event:self.select_up(event),"+")
        self.container.bind('<Down>',lambda event:self.select_down(event),"+")
        self.container.bind('<Delete>',lambda event:self.del_select(event),"+")
        # 容器高度
        self.container_height = 0
        # 内容物
        self.content = content
        # 容器内的元件，顺序
        self.element = {}
        self.element_keys = []
        # 当前选中的对象
        self.selected:list = []
    def get_container_height(self)->int:
        return 0
    def update_item(self):
        # 重设容器高度：# BUG：会导致闪烁！
        this_height = self.get_container_height()
        if self.container_height != this_height:
            self.config(height=this_height)
            self.container_height = this_height
        # 清空原件
        for ele in self.element_keys:
            self.element[ele].place_forget()
    def select_item(self,event,index,add=False):
        self.container.focus_set()
        # 根据点击的y，定位本次选中的
        selected_idx = index
        if selected_idx in self.element_keys:
        # if selected_idx in self.element.keys():
            if add is not True:
                # 先清空选中的列表
                for idx in self.selected:
                    self.element[idx].drop_select()
                self.selected.clear()
            # 添加本次选中的
            if index not in self.selected:
                self.element[selected_idx].get_select()
                self.selected.append(selected_idx)
            # 尝试预览
            self.preview_select()
    def select_up(self,event):
        # top 顶部，初始值是所有元素的总长度
        top = len(self.element_keys)
        # 找到当前选中的所有元素的顶部
        for sele in self.selected:
            idx_this = self.element_keys.index(sele)
            if idx_this < top:
                top = idx_this
        if top == len(self.element_keys):
            pass
        elif top == 0:
            self.select_item(None,self.element_keys[0])
        else:
            self.select_item(None,self.element_keys[top-1])
    def select_down(self,event):
        # top 顶部，初始值是-1
        bottom = -1
        # 找到当前选中的所有元素的顶部
        for sele in self.selected:
            idx_this = self.element_keys.index(sele)
            if idx_this > bottom:
                bottom = idx_this
        if bottom == -1:
            pass
        elif bottom == len(self.element_keys)-1:
            self.select_item(None,self.element_keys[-1])
        else:
            self.select_item(None,self.element_keys[bottom+1])
    def select_range(self,event,index:str):
        self.container.focus_set()
        if index == False:
            # effect_range = self.element.keys()
            effect_range = self.element_keys
        else:
            # 上一个选中的，数字序号
            # last_selected_idx:int = int(self.selected[-1]) # 最后一个
            last_selected_idx:int = self.element_keys.index(self.selected[-1])
            # 本次选中的，数字序号
            this_selected_idx:int = self.element_keys.index(index)
            # this_selected_idx:int = int(index)
            # 正序或是倒序
            if this_selected_idx > last_selected_idx:
                effect_range = [self.element_keys[idx] for idx in range(last_selected_idx+1, this_selected_idx+1)]
            else:
                effect_range = [self.element_keys[idx] for idx in range(this_selected_idx, last_selected_idx)]
            # range(this_selected_idx,last_selected_idx,{True:1,False:-1}[last_selected_idx>=this_selected_idx])
        # 先清除所有已选择，再重新选择：不应该在这里操作
        # self.selected.clear()
        for idx in effect_range:
            if idx not in self.selected:
                self.select_item(event=event,index=str(idx),add=True)
    def preview_select(self):
        if len(self.selected) == 1:
            to_preview = self.selected[0]
            self.preview_canvas.preview(to_preview)
    def reindex(self):
        # 重新设置序号，正常是不需要的
        # 待RGL类重载
        pass
    def del_select(self,event):
        # print(self.selected)
        for sele in self.selected:
            # 删除section_element
            self.element_keys.remove(sele)
            self.element.pop(sele).destroy()
            self.content.delete(sele)
        self.selected.clear()
        self.reindex()
        self.update_item()
class RGLContainer(Container):
    def __init__(self,master,content:RplGenLog,screenzoom):
        # 初始化基类
        super().__init__(master=master,content=content,screenzoom=screenzoom)
        # 根据内容物，调整容器总高度
        # self.container_height = int(60*self.sz)*len(self.content.struct)
        # self.config(height=int(60*self.sz)*len(self.content.struct))
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            self.element_keys.append(key)
            self.element[key] = RGLSectionElement(
                master=self,
                bootstyle='primary',
                text=key,
                section=this_section,
                screenzoom=self.sz)
        # 将内容物元件显示出来
        self.update_item()
    def get_container_height(self) -> int:
        return int(60*self.sz)*len(self.element_keys)
    # TODO: RGL的list必须是有序的！如果发生了新建、删除，需要重新给所有小节标号！
    def reindex(self):
        new_element_keys = [str(x) for x in range(0,len(self.element_keys))]
        new_element:dict = {}
        for idx,ele in enumerate(self.element_keys):
            this_new = new_element_keys[idx]
            new_element[this_new] = self.element[ele]
            new_element[this_new].update_index(this_new)
        # 更新
        self.element = new_element
        self.element_keys = new_element_keys
        self.content.reindex()
        return 1
    def update_item(self):
        super().update_item()
        SZ_60 = int(self.sz * 60)
        SZ_55 = int(self.sz * 55)
        sz_10 = int(self.sz * 10)
        for idx,key in enumerate(self.element_keys):
            this_section_frame:ttk.LabelFrame = self.element[key]
            this_section_frame.place(x=0,y=idx*SZ_60,width=-sz_10,height=SZ_55,relwidth=1)
class MDFContainer(Container):
    def __init__(self,master,content:MediaDef,typelist:list,screenzoom):
        # 初始化基类
        super().__init__(master=master,content=content,screenzoom=screenzoom)
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            if this_section['type'] not in typelist:
                continue
            self.element_keys.append(key)
            self.element[key] = MDFSectionElement(
                master=self,
                bootstyle='secondary',
                text=key,
                section=this_section,
                screenzoom=self.sz)
        # 根据内容物，调整容器总高度
        # self.config(height=int(200*self.sz*np.ceil(len(self.element_keys)/3)))
        # 将内容物元件显示出来
        self.update_item()
    def get_container_height(self) -> int:
        return int(200*self.sz*np.ceil(len(self.element_keys)/3))
    def update_item(self):
        super().update_item()
        SZ_100 = int(self.sz * 200)
        SZ_95 = int(self.sz * 190)
        sz_10 = int(self.sz * 10)
        for idx,key in enumerate(self.element_keys):
            this_section_frame:ttk.LabelFrame = self.element[key]
            this_section_frame.place(relx=idx%3 * 0.33,y=idx//3*SZ_100,width=-sz_10,height=SZ_95,relwidth=0.33)
class CTBContainer(Container):
    def __init__(self,master,content:CharTable,name:str,screenzoom):
        # 初始化基类
        super().__init__(master=master,content=content,screenzoom=screenzoom)
        # 可引用对象
        self.ref_medef = self.master.master.ref_medef
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            if this_section['Name'] != name:
                continue
            self.element_keys.append(key)
            self.element[key] = CTBSectionElement(
                master=self,
                bootstyle='primary',
                text=key,
                section=this_section,
                screenzoom=self.sz
                )
        # 根据内容物，调整容器总高度
        # self.config(height=int(100*self.sz*len(self.element_keys)))
        # 将内容物元件显示出来
        self.update_item()
    def get_container_height(self) -> int:
        return int(100*self.sz*len(self.element_keys))
    def update_item(self):
        super().update_item()
        SZ_100 = int(self.sz * 100)
        SZ_95 = int(self.sz * 95)
        sz_10 = int(self.sz * 10)
        for idx,key in enumerate(self.element_keys):
            this_section_frame:ttk.LabelFrame = self.element[key]
            this_section_frame.place(x=0,y=idx*SZ_100,width=-sz_10,height=SZ_95,relwidth=1)
# 容器中的每个小节
class SectionElement:
    MDFscript = MediaDef()
    RGLscript = RplGenLog()
    CTBscript = CharTable()
    def get_select(self):
        SZ_5 = int(self.sz * 5)
        self.select_symbol.place(x=0,y=0,width=SZ_5,relheight=1)
    def drop_select(self):
        self.select_symbol.place_forget()
    def update_image_from_section(self,section,icon_size:int,thumbname='%d'):
        # icon_size= int(160*self.sz)
        # 确认显示内容:image
        if   section['type'] in ['Animation','Bubble','Balloon','DynamicBubble','ChatWindow','Background']:
            if section['filepath'] in self.thumbnail_name.keys():
                self.thumb = self.thumbnail_name[section['filepath']]
            else:
                # 新建一个缩略图
                if section['filepath'] in [None,'None']:
                    image = Image.new(mode='RGBA',size=(icon_size,icon_size),color=(0,0,0,0))
                elif section['filepath'] in MediaObj.cmap.keys():
                    image = Image.new(mode='RGBA',size=(icon_size,icon_size),color=MediaObj.cmap[filepath])
                else:
                    filepath = Filepath(filepath=section['filepath']).exact()
                    image = Image.open(filepath)
                # 缩略名
                thumbnail_name_this = thumbname%self.thumbnail_idx
                self.__class__.thumbnail_idx += 1
                # 应用
                self.thumbnail_name[section['filepath']] = thumbnail_name_this
                self.thumbnail_image[section['filepath']] = ImageTk.PhotoImage(name=thumbnail_name_this,image=thumbnail(image=image,icon_size=icon_size))
                self.thumb = thumbnail_name_this
        elif self.line_type in ['Text','StrokeText','RichText']:
            # 新建一个缩略图
            text_obj = self.MDFscript.instance_execute(section)
            temp_canvas = pygame.Surface(size=(icon_size,icon_size))
            # 背景图的颜色
            if self.line_type == 'StrokeText':
                if np.mean(text_obj.edge_color) > 230:
                    temp_canvas.fill('black')
                else:
                    temp_canvas.fill('white')
            else:
                if np.mean(text_obj.color) > 230:
                    temp_canvas.fill('black')
                else:
                    temp_canvas.fill('white')
            # 渲染预览字体
            test_text = {'Text':'字体#Text','StrokeText':'描边#Stroke','RichText':'[i]富文[#][/i][u]Rich'}[self.line_type]
            for idx,text in enumerate(text_obj.draw(text=test_text)):
                text:pygame.Surface
                w,h = text.get_size()
                temp_canvas.blit(
                    text,
                    [
                        int( icon_size/2 - w/2 ),
                        int( icon_size/2 - (1 - idx) * text_obj.size )
                    ]
                )
            # 转为Image
            image = Image.frombytes(mode='RGB',size=(icon_size,icon_size),data=pygame.image.tostring(temp_canvas,'RGB'))
            # 缩略名
            thumbnail_name_this = 'thumbnail%d'%self.thumbnail_idx
            self.__class__.thumbnail_idx += 1
            # 应用
            self.thumbnail_name[thumbnail_name_this] = thumbnail_name_this
            self.thumbnail_image[thumbnail_name_this] = ImageTk.PhotoImage(name=thumbnail_name_this,image=thumbnail(image=image,icon_size=icon_size))
            self.thumb = thumbnail_name_this
        elif self.line_type in ['Audio','BGM']:
            if self.line_type not in self.thumbnail_name.keys():
                self.__class__.thumbnail_image['Audio'] = ImageTk.PhotoImage(name='Audio', image=Image.open('./media/icon/audio.png').resize([icon_size,icon_size]))
                self.__class__.thumbnail_image['BGM']   = ImageTk.PhotoImage(name='BGM',   image=Image.open('./media/icon/bgm.png').resize([icon_size,icon_size]))
                self.thumbnail_name['Audio'] = 'Audio'
                self.thumbnail_name['BGM'] = 'BGM'
            self.thumb = self.line_type
        elif self.line_type in ['Pos','PosGrid','FreePos']:
            if self.line_type not in self.thumbnail_name.keys():
                self.__class__.thumbnail_image['Pos']        = ImageTk.PhotoImage(name='Pos',    image=Image.open('./media/icon/Pos.png').resize([icon_size,icon_size]))
                self.__class__.thumbnail_image['PosGrid']    = ImageTk.PhotoImage(name='PosGrid',image=Image.open('./media/icon/PosGrid.png').resize([icon_size,icon_size]))
                self.__class__.thumbnail_image['FreePos']    = ImageTk.PhotoImage(name='FreePos',image=Image.open('./media/icon/FreePos.png').resize([icon_size,icon_size]))
                self.thumbnail_name['Pos'] = 'Pos'
                self.thumbnail_name['PosGrid'] = 'PosGrid'
                self.thumbnail_name['FreePos'] = 'FreePos'
            self.thumb = self.line_type
        return self.thumb

class RGLSectionElement(ttk.LabelFrame,SectionElement):
    def __init__(self,master,bootstyle,text,section:dict,screenzoom):
        self.sz = screenzoom
        self.line_type = section['type']
        self.idx = text # 序号
        super().__init__(master=master,bootstyle=bootstyle,text=self.idx,labelanchor='e')
        # 从小节中获取文本
        self.update_text_from_section(section=section)
        self.items = {
            'head' : ttk.Label(master=self,text=self.header,anchor='w',style=self.hstyle+'.TLabel'),
            'sep'  : ttk.Separator(master=self),
            'main' : ttk.Label(master=self,text=self.main,anchor='w',style=self.mstyle+'.TLabel'),
        }
        self.select_symbol = ttk.Frame(master=self,bootstyle='primary')
        self.update_item()
    def update_text_from_section(self,section):
        # 确认显示内容
        if   self.line_type == 'blank':
            self.header = '空行'
            self.main = ''
            self.hstyle = 'comment'
            self.mstyle = 'ingore'
        elif self.line_type == 'comment':
            self.header = '# 注释'
            self.main = section['content']
            self.hstyle = 'comment'
            self.mstyle = 'ingore'
        elif self.line_type == 'dialog':
            # 如果是默认，那么仅显示名字
            if section['charactor_set']['0']['subtype'] == 'default':
                self.header = '[{}]'.format(
                    section['charactor_set']['0']['name']
                )
            else:
                self.header = '[{}.{}]'.format(
                    section['charactor_set']['0']['name'],
                    section['charactor_set']['0']['subtype']
                    )
            # 主文本
            self.main = section['content']
            self.hstyle = 'dialog'
            self.mstyle = 'main'
            # 显示星标
            if '*' in section['sound_set'].keys():
                self.header = '★ ' + self.header
            elif '{*}' in section['sound_set'].keys():
                self.header = '★ ' + self.header
                self.hstyle = 'invasterisk'
            else:
                self.mstyle = 'main'
        elif self.line_type == 'background':
            self.header = '<放置背景>'
            self.main = section['object']
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'animation':
            self.header = '<放置立绘>'
            self.main = self.RGLscript.anime_export(section['object'])
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'bubble':
            self.header = '<放置气泡>'
            self.main = self.RGLscript.bubble_export(section['object'])
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'set':
            target,unit = {
                #默认切换效果（立绘）
                'am_method_default' : ['默认切换效果-立绘',''],
                #默认切换效果持续时间（立绘）
                'am_dur_default'    : ['默认切换时间-立绘',' 帧'],
                #默认切换效果（文本框）
                'bb_method_default' : ['默认切换效果-气泡',''],
                #默认切换效果持续时间（文本框）
                'bb_dur_default'    : ['默认切换时间-气泡',' 帧'],
                #默认切换效果（背景）
                'bg_method_default' : ['默认切换效果-背景',''],
                #默认切换时间（背景）
                'bg_dur_default'    : ['默认切换时间-背景',' 帧'],
                #默认文本展示方式
                'tx_method_default' : ['默认文本展示效果',''],
                #默认单字展示时间参数
                'tx_dur_default'    : ['默认单字时间',' 帧/字'],
                #语速，单位word per minute
                'speech_speed'      : ['缺省星标时的语速',' 字/分钟'],
                #默认的曲线函数
                'formula'           : ['动画函数的曲线',''],
                # 星标音频的句间间隔 a1.4.3，单位是帧，通过处理delay
                'asterisk_pause'    : ['星标小节的间距时间',' 帧'],
                # a 1.8.8 次要立绘的默认透明度
                'secondary_alpha'   : ['次要角色立绘的默认透明度',' %'],
                # 对话行内指定的方法的应用对象：animation、bubble、both、none
                'inline_method_apply' : ['对话行内效果的应用范围','']
            }[section['target']]
            self.header = '<设置：' + target + '>'
            if section['value_type'] == 'digit':
                value = str(section['value'])
                self.mstyle = 'digit'
            elif section['value_type'] in ['function','enumerate']:
                value = section['value']
                self.mstyle = 'fuction'
            elif section['value_type'] == 'method':
                value = self.RGLscript.method_export(section['value'])
                self.mstyle = 'method'
            else:
                value = '错误'
                self.mstyle = 'exception'
            self.main = value + unit
            # 判断类型
            self.hstyle = 'setdync'
        elif self.line_type == 'move':
            self.header = '<移动：' + section['target'] + '>'
            self.main = self.RGLscript.move_export(section['value'])
            self.hstyle = 'setdync'
            self.mstyle = 'object'
        elif self.line_type == 'table':
            if section['target']['subtype'] is None:
                target = section['target']['name'] +'.'+ section['target']['column']
            else:
                target = section['target']['name'] +'.'+ section['target']['subtype'] +'.'+ section['target']['column']
            self.header = '<表格：' + target + '>'
            self.main = str(section['value'])
            self.hstyle = 'setdync'
            self.mstyle = 'main'
        elif self.line_type == 'music':
            self.header = '<背景音乐>'
            self.main = str(section['value'])
            self.hstyle = 'setdync'
            self.mstyle = 'object'
        elif self.line_type == 'clear':
            self.header = '<清除>'
            self.main = section['object']
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'hitpoint':
            self.header = '<生命动画>'
            self.main = '({},{},{},{})'.format(
                section['content'],
                section['hp_max'],
                section['hp_begin'],
                section['hp_end']
                )
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'dice':
            self.header = '<骰子动画>'
            self.main = self.RGLscript.dice_export(section['dice_set'])
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'wait':
            self.header = '<停顿>'
            self.main = str(section['time']) + ' 帧'
            self.hstyle = 'place'
            self.mstyle = 'digit'
    def update_index(self,new_index):
        new_index = str(new_index)
        self.idx = new_index
        self.config(text=new_index)
    def update_item(self):
        for idx,key in enumerate(self.items):
            this_item:ttk.Label = self.items[key]
            this_item.pack(fill='x',anchor='w',side='top',expand={'head':False,'sep':False,'main':True}[key])
            # 按键点击事件
            this_item.bind('<Button-1>',lambda event:self.master.select_item(event,index=self.idx,add=False))
            this_item.bind('<Control-Button-1>',lambda event:self.master.select_item(event,index=self.idx,add=True))
            this_item.bind('<Shift-Button-1>',lambda event:self.master.select_range(event,index=self.idx))
class MDFSectionElement(ttk.Frame,SectionElement):
    MDFscript = MediaDef()
    thumbnail_image = {}
    thumbnail_name = {}
    thumbnail_idx = 0
    def __init__(self,master,bootstyle,text,section:dict,screenzoom):
        self.sz = screenzoom
        self.line_type = section['type']
        self.name = text # 序号
        super().__init__(master=master,bootstyle=bootstyle,borderwidth=int(1*self.sz))
        # 颜色标签
        if 'label_color' not in section.keys():
            self.labelcolor = 'Lavender'
        elif section['label_color'] is None:
            self.labelcolor = 'Lavender'
        else:
            self.labelcolor = section['label_color']
        # 从小节中获取缩略图
        self.update_image_from_section(section=section)
        self.items = {
            'head' : ttk.Label(master=self,text=self.name,anchor='center',style=self.labelcolor+'.TLabel'),
            'thumbnail' : ttk.Label(master=self,image=self.thumb,anchor='center')
        }
        # 被选中的标志
        self.select_symbol = ttk.Frame(master=self,bootstyle='primary')
        self.update_item()
    def update_image_from_section(self,section):
        icon_size= int(160*self.sz)
        return super().update_image_from_section(section=section,icon_size=icon_size,thumbname='MDFthumb%d')
    def update_item(self):
        for idx,key in enumerate(self.items):
            this_item:ttk.Label = self.items[key]
            this_item.pack(fill='both',anchor='w',side='top',expand={'head':False,'thumbnail':True}[key])
            # 按键点击事件
            this_item.bind('<Button-1>',lambda event:self.master.select_item(event,index=self.name,add=False))
            this_item.bind('<Control-Button-1>',lambda event:self.master.select_item(event,index=self.name,add=True))
            this_item.bind('<Shift-Button-1>',lambda event:self.master.select_range(event,index=self.name))
class CTBSectionElement(ttk.Frame,SectionElement):
    thumbnail_image = {}
    thumbnail_name = {}
    thumbnail_idx = 0
    def __init__(self,master,bootstyle,text,section:dict,screenzoom):
        self.sz = screenzoom
        icon_size = int(self.sz * 93)
        self.name = text # 序号
        super().__init__(master=master,bootstyle=bootstyle,borderwidth=int(1*self.sz))
        self.section = section
        # 媒体定义对象
        self.ref_medef:MediaDef = self.master.ref_medef
        # 容器
        self.table = ttk.Frame(master=self,bootstyle=bootstyle,borderwidth=0)
        self.thumbnail = ttk.Frame(master=self,bootstyle=bootstyle,borderwidth=0)
        # 缩略图
        am_thumbname = self.update_image_from_section(media_name=section['Animation'])
        bb_thumbname = self.update_image_from_section(media_name=section['Bubble'])
        self.items = {
            'head'  : ttk.Label(master=self.table,text=self.name,style='CharHead.TLabel'),
            'anime' : ttk.Label(master=self.table,text='立绘：'+self.section['Animation'],style='main.TLabel'),
            'bubble': ttk.Label(master=self.table,text='气泡：'+self.section['Bubble'],style='main.TLabel'),
            'voice' : ttk.Label(master=self.table,text='语音：'+self.section['Voice']+'|'+str(self.section['SpeechRate'])+'|'+str(self.section['PitchRate']),style='main.TLabel'),
            'AMThB' : ttk.Label(master=self.thumbnail,image=am_thumbname,anchor='center',padding=0),
            'BBThB' : ttk.Label(master=self.thumbnail,image=bb_thumbname,anchor='center',padding=0)
        }
        # 被选中的标志
        self.select_symbol = ttk.Frame(master=self,bootstyle='primary')
        self.update_item()
    def update_item(self):
        SZ_95 = int(self.sz * 95)
        SZ_1 = int(self.sz *1)
        # 元件
        self.items['head'].place(relx=0,rely=0,relheight=0.33,relwidth=1)
        self.items['anime'].place(relx=0,rely=0.33,relheight=0.33,relwidth=0.5)
        self.items['bubble'].place(relx=0.5,rely=0.33,relheight=0.33,relwidth=0.5)
        self.items['voice'].place(relx=0,rely=0.67,relheight=0.33,relwidth=1)
        self.items['AMThB'].place(x=0,y=0,width=SZ_95-2*SZ_1,height=SZ_95-2*SZ_1)
        self.items['BBThB'].place(x=SZ_95-SZ_1,y=0,width=SZ_95-2*SZ_1,height=SZ_95-2*SZ_1)
        # 容器
        self.table.place(x=2*SZ_95-2*SZ_1,y=0,width=-2*SZ_95+2*SZ_1,relwidth=1,relheight=1)
        self.thumbnail.place(x=0,y=0,width=2*SZ_95-2*SZ_1,relheight=1)
        for idx,key in enumerate(self.items):
            this_item:ttk.Label = self.items[key]
            # 按键点击事件
            this_item.bind('<Button-1>',lambda event:self.master.select_item(event,index=self.name,add=False))
            this_item.bind('<Control-Button-1>',lambda event:self.master.select_item(event,index=self.name,add=True))
            this_item.bind('<Shift-Button-1>',lambda event:self.master.select_range(event,index=self.name))
    def update_image_from_section(self,media_name:str)->str:
        # 图标大小
        icon_size = int(self.sz * 93)
        # 媒体名是":"前面的部分
        media_name = media_name.split(':')[0]
        # 是否存在
        if media_name == 'NA':
            if 'NA' not in self.thumbnail_name.keys():
                self.thumbnail_image['NA'] = ImageTk.PhotoImage(name='NA', image=Image.open('./media/icon/NA.png').resize([icon_size,icon_size]))
                self.thumbnail_name['NA'] = 'NA'
            return 'NA'
        if media_name not in self.ref_medef.struct.keys():
            return 'MediaNotFound' # TODO : 给这个错误情况来一个图标（伊可的）
        else:
            section_this:dict = self.ref_medef.struct[media_name]
        # 是否是Am或者Bb
        if section_this['type'] not in ['Animation','Bubble','Balloon','DynamicBubble','ChatWindow']:
            return 'MediaNotFound'
        else:
            return super().update_image_from_section(section=section_this,icon_size=icon_size,thumbname='CTBthumb%d')