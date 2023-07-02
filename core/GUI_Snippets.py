#!/usr/bin/env python
# coding: utf-8

# 代码补全工具

import re
import tkinter as tk
import ttkbootstrap as ttk
from chlorophyll import CodeView
from .ScriptParser import CharTable, MediaDef

class RGLSnippets(ttk.Menu):
    Snippets = {
        "command":{
            "dialog"        :['对话行','[]:',1],
            "wait"          :['停顿','<wait>:',7],
            "background"    :['切换背景','<background>:',13],
            "animation"     :['显示立绘','<animation>:()',13],
            "bubble"        :['显示气泡','<bubble>:',9],
            "BGM"           :['背景音乐','<BGM>:',6],
            "set"           :['设置','<set:>:',5],
            "table"         :['修改角色表','<table:>:',7],
            "move"          :['移动媒体','<move:>:',6],
            "clear"         :['清空聊天窗','<clear>:',8],
            "hitpoint"      :['血量动画','<hitpoint>:(描述,10,10,10)',14],
            "dice"          :['骰子动画','<dice>:(描述,100,50,75),(描述,100,50,25)',10],
            "comment"       :['注释','# ',2]
        },
        "set":{
            "am_method_default"     :["默认切换效果-立绘","am_method_default",19],
            "bb_method_default"     :["默认切换效果-气泡","bb_method_default",19],
            "bg_method_default"     :["默认切换效果-背景","bg_method_default",19],
            "tx_method_default"     :["默认文字效果","tx_method_default",19],
            "speech_speed"          :["无语音句子的语速","speech_speed",14],
            "asterisk_pause"        :["星标间隔时间","asterisk_pause",16],
            "secondary_alpha"       :["默认次要立绘透明度","secondary_alpha",17],
            "inline_method_apply"   :["对话行类效果的作用对象","inline_method_apply",21],
            "am_dur_default"        :["默认切换时间-立绘","am_dur_default",16],
            "bb_dur_default"        :["默认切换时间-气泡","bb_dur_default",16],
            "bg_dur_default"        :["默认切换时间-背景","bg_dur_default",16],
            "tx_dur_default"        :["默认文字效果时间","tx_dur_default",16],
            "formula"               :["动画曲线","formula",9],
        },
        "am_dur":{
            "0"    : ["0","0",1],
            "10"    : ["10","10",2],
            "20"    : ["20","20",2],
            "30"    : ["30","30",2],
            "60"    : ["60","60",2],
            "100"   : ["100","100",3],
        },
        "tx_dur":{
            "1"     : ["1","1",1],
            "2"     : ["2","2",1],
            "3"     : ["3","3",1],
            "10"    : ["10","10",2],
            "30"    : ["30","30",2],
        },
        "speed":{
            "220"   : ["220","220",3],
            "300"   : ["300","300",3],
            "600"   : ["600","600",3],
            "900"   : ["900","900",3],
            "1800"  : ["1800","1800",4],
        },
        "formula":{
            "linear"    : ["线性","linear",6],
            "quadratic" : ["二次","quadratic",9],
            "quadraticR": ["反二次","quadraticR",10],
            "sigmoid"   : ["正S形","sigmoid",7],
            "right"     : ["右S形","right",5],
            "left"      : ["左S形","left",4],
            "sincurve"  : ["正弦","sincurve",8],
        },
        "inline":{
            "both"      : ["全部","both",4],
            "amimation" : ["立绘","animation",9],
            "bubble"    : ["气泡","bubble",6],
            "none"      : ["禁用","none",4],
        },
        "tx_met":{
            "all"   : ["全部","<all=>",5],
            "w2w"   : ["逐字","<w2w=>",5],
            "s2s"   : ["逐句","<s2s=>",5],
            "l2l"   : ["逐行","<l2l=>",5],
            "run"   : ["滚动","<run=>",5],
        },
        "bg_met":{
            "replace"   : ["直接替换","<replace=>",9],
            "delay"     : ["延迟替换","<delay=>",7],
            "cross"     : ["交叉溶解","<cross=>",7],
            "black"     : ["黑场","<black=>",7],
            "white"     : ["白场","<white=>",7],
            "push"      : ["推入","<push=>",6],
            "cover"     : ["覆盖","<cover=>",7],
        },
        "ab_met":{
            "replace"   : ["直接替换","<replace=>",9],
            "cross"     : ["交叉溶解","<cross=>",7],
            "black"     : ["淡入淡出","<black=>",7],
            "pass"      : ["左进右出","<black_pass_left_minor=>",23],
            "leap"      : ["上进上出","<black_leap_down_minor=>",23]
        },
    }
    def __init__(self, master, mediadef:MediaDef, chartab:CharTable):
        # 初始化菜单
        super().__init__(master=master, tearoff=0, font=('Sarasa Mono SC',10)) # FIXME：注意，这里指定使用更纱黑体的话，会导致第一次启动时延迟约半秒
        self.codeview:CodeView = master
        # 引用媒体
        self.ref_media = mediadef
        self.ref_char = chartab
        # 光标位置
        index_,x,y = self.get_insert_curser()
        self.curser_idx = index_
        self.curser_pos = (x,y)
        # 初始化
        self.parse_up_down_stream()
        # 显示
        self.post(
            x = self.codeview.winfo_rootx()+self.curser_pos[0],
            y = self.codeview.winfo_rooty()+self.curser_pos[1]
            )
    # 获取当前光标位置
    def get_insert_curser(self):
        index_ = self.codeview.index('insert')
        x, y, _, _ = self.codeview.bbox(index_)
        return index_,x,y
    # 获取上下文
    def parse_up_down_stream(self):
        row,col = self.curser_idx.split('.')
        # 当前行的全部内容
        text_this = self.codeview.get(f'{row}.0', f'{row}.end')
        text_upstream = text_this[:int(col)]
        text_downstream = text_this[int(col):]
        # 如果是空行开头
        if text_upstream == '' and text_downstream == '':
            self.init_snippets_options('command')
        # 对话行添加
        elif re.fullmatch('^\[([\w\ \.\(\)]+,)*',text_upstream):
            self.init_snippets_options('charactor')
        # 差分添加
        elif re.fullmatch('^\[([\w\ \.\(\)]+,)*([\w\ ]+(\(\d+\))?)\.',text_upstream):
            # 提取角色名
            name = re.fullmatch('^\[([\w\ \.\(\)]+,)*([\w\ ]+(\(\d+\))?)\.',text_upstream).group(2)
            self.init_snippets_options('subtype',name=name)
        # 停顿
        elif text_upstream == '<wait>:' and text_downstream == '':
            self.init_snippets_options('am_dur')
        # 背景、立绘、气泡、bgm
        elif re.fullmatch('<background>(<\w+(=\d+)?>)?:',text_upstream) and text_downstream == '':
            self.init_snippets_options('background')
        elif re.fullmatch('<animation>(<\w+(=\d+)?>)?:\(?(\w+,)*',text_upstream):
            self.init_snippets_options('animation')
        elif re.fullmatch('<bubble>(<\w+(=\d+)?>)?:',text_upstream) and text_downstream == '':
            self.init_snippets_options('bubble')
        elif re.fullmatch('<(BGM|bgm)>:',text_upstream) and text_downstream == '':
            self.init_snippets_options('bgm')
        # 音效
        elif re.fullmatch('^\[[\w\ \.\,\(\)]+\](<\w+(=\d+)>)?:[^\\"]+',text_upstream) and text_downstream=='':
            # 检查上游是否已经包含了星标了
            if text_upstream[-1] in ['>','}']:
                if re.findall('{.*?\*.*?}',text_upstream):
                    self.init_snippets_options('audio',asterisk=False)
                else:
                    self.init_snippets_options('audio',asterisk=True)
            else:
                self.init_snippets_options('audio|tx_met')
        elif re.fullmatch('^\[[\w\ \.\,\(\)]+\](<\w+(=\d+)>)?:[^\\"]+\{\w+;',text_upstream) and text_downstream[0]=='}':
            self.init_snippets_options('am_dur')
        # 文字效果

        # 清除
        elif text_upstream == '<clear>:' and text_downstream == '':
            self.init_snippets_options('chatwindow')
        # 设置
        elif text_upstream == '<set:' and text_downstream[0:2]=='>:':
            self.init_snippets_options('set')
        elif re.fullmatch('^<set:(\w+)>:',text_upstream) and text_downstream=='':
            to_set = re.fullmatch('^<set:(\w+)>:',text_upstream).group(1)
            if to_set in ['am_dur_default','bb_dur_default','bg_dur_default','asterisk_pause','secondary_alpha']:
                self.init_snippets_options('am_dur')
            elif to_set in ['am_method_default','bb_method_default']:
                self.init_snippets_options('ab_met')
            elif to_set == 'bg_method_default':
                self.init_snippets_options('bg_met')
            elif to_set == 'tx_dur_default':
                self.init_snippets_options('tx_dur')
            elif to_set == 'tx_method_default':
                self.init_snippets_options('tx_met')
            elif to_set == 'formula':
                self.init_snippets_options('formula')
            elif to_set == 'inline_method_apply':
                self.init_snippets_options('inline')
            elif to_set == 'speech_speed':
                self.init_snippets_options('speed')
        # 移动
        elif text_upstream == '<move:' and text_downstream[0:2]=='>:':
            self.init_snippets_options('move')
        elif re.fullmatch("^<move:(\w+)>:(.+)?",text_upstream) and text_downstream == '':
            self.init_snippets_options('posexp') # FIXME
        # 效果
        elif text_upstream == '<background>' and text_downstream[0]==':':
            self.init_snippets_options('bg_met')
        elif text_upstream in ['<animation>','bubble'] or re.fullmatch('^\[[\w\ \.\,\(\)]+\]',text_upstream) and text_downstream[0]==':':
            self.init_snippets_options('ab_met')
        elif re.fullmatch("(.+)<(\w+)=",text_upstream) and text_downstream[0]=='>':
            method = re.fullmatch("(.+)<(\w+)=",text_upstream).group(2)
            if method in ['w2w','l2l','s2s','all']:
                self.init_snippets_options('tx_dur')
            else:
                self.init_snippets_options('am_dur')
    def init_snippets_options(self,type_='command',**kw_args):
        self.snippets_type = type_
        # 行命令
        if self.snippets_type in ['command','set','am_dur','tx_dur','formula','inline','speed','bg_met','ab_met','tx_met']:
            self.snippets_content = self.Snippets[self.snippets_type]
            for keyword in self.snippets_content:
                option, snippet, cpos = self.snippets_content[keyword]
                self.add_command(label=option, command=self.insert_snippets(snippet, cpos))
            # 立绘切换效果的特殊之处
            if self.snippets_type == 'ab_met':
                self.add_command(label='（自定义）',command=self.custom_ab_method())
        # 角色联想
        elif self.snippets_type=='charactor':
            list_of_snippets = self.ref_char.get_names()
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 差分联想
        elif self.snippets_type=='subtype':
            char_name = kw_args['name']
            list_of_snippets = self.ref_char.get_subtype(char_name)
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 背景
        elif self.snippets_type=='background':
            self.add_command(label='（黑）', command=self.insert_snippets("black", 5))
            self.add_command(label='（白）', command=self.insert_snippets("white", 5))
            list_of_snippets = self.ref_media.get_type('background')
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 立绘
        elif self.snippets_type=='animation':
            self.add_command(label='（无）', command=self.insert_snippets("NA", 2))
            list_of_snippets = self.ref_media.get_type('anime')
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 气泡联想，聊天窗以对象而不是关键字的形式返回
        elif self.snippets_type=='bubble':
            self.add_command(label='（无）', command=self.insert_snippets("NA", 2))
            list_of_snippets = self.ref_media.get_type('bubble',cw=False) + self.ref_media.get_type('chatwindow')
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name+'("","")', len(name)+2))
        # 背景音乐
        elif self.snippets_type=='bgm':
            self.add_command(label='（停止）', command=self.insert_snippets("stop", 4))
            list_of_snippets = self.ref_media.get_type('bgm')
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 音效
        elif self.snippets_type=='audio':
            if kw_args['asterisk']:
                self.add_command(label='（语音合成）', command=self.insert_snippets("{*}", 3))
            else:
                self.add_command(label='（语音合成）', command=self.insert_snippets("{*}", 3), state='disabled')
            self.add_command(label='（无）', command=self.insert_snippets(r"{NA}", 4))
            list_of_snippets = self.ref_media.get_type('audio')
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets("{"+name+"}", len(name)+2))
        # 清除对话框
        elif self.snippets_type=='chatwindow':
            list_of_snippets = self.ref_media.get_type('chatwindow')
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 移动
        elif self.snippets_type=='move':
            list_of_snippets = self.ref_media.get_moveable()
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        elif self.snippets_type=='posexp':
            # TODO 位置表达式！
            pass
        # 音效和文字效果组合
        elif self.snippets_type=='audio|tx_met':
            self.add_command(label='（语音合成）', command=self.insert_snippets("{*}", 3))
            self.add_separator()
            tx_met_menu = ttk.Menu(master=self)
            audio_menu = ttk.Menu(master=self)
            self.add_cascade(label='文字效果',menu=tx_met_menu)
            self.add_cascade(label='音效',menu=audio_menu)
            # 文字效果
            dict_of_snippets = self.Snippets['tx_met']
            for keyword in dict_of_snippets:
                option, snippet, cpos = dict_of_snippets[keyword]
                tx_met_menu.add_command(label=option, command=self.insert_snippets(snippet, cpos))
            # 音效
            audio_menu.add_command(label='（无）', command=self.insert_snippets(r"{NA}", 4))
            list_of_snippets = self.ref_media.get_type('audio')
            for name in list_of_snippets:
                audio_menu.add_command(label=name, command=self.insert_snippets("{"+name+"}", len(name)+2))
    # 闭包
    def insert_snippets(self, snippet, cpos):
        # 命令内容
        def command():
            self.codeview.insert(self.curser_idx,chars=snippet)
            self.codeview.mark_set("insert",f'{self.curser_idx}+{cpos}c')
            self.codeview.highlight_all()
        return command
    # 自定义切换效果
    def custom_ab_method(self):
        pass