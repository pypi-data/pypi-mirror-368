import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from DrissionPage import ChromiumPage
from DrissionPage.errors import ElementNotFoundError
import time
import threading
import pandas as pd
import json
from datetime import datetime
import os
from urllib.parse import quote
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import traceback
import re
import requests
import logging
import webbrowser

class DouyinAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("抖音作品分析工具")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # 设置主题颜色
        self.primary_color = "#FF2E63"  # 抖音红
        self.secondary_color = "#08D9D6"  # 抖音蓝绿
        self.bg_color = "#F5F5F5"  # 背景灰
        self.text_color = "#333333"  # 文字深灰
        self.highlight_color = "#FF9A3C"  # 强调色
        
        # 配置样式
        self.configure_styles()
        
        # 创建变量
        self.url = tk.StringVar(value="https://www.douyin.com")
        self.scroll_count = tk.StringVar(value="100")
        self.delay = tk.StringVar(value="2")
        self.browser_path = tk.StringVar(value=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        self.is_running = False
        self.collected_data = []
        self.page = None  # DrissionPage实例
        
        # 加载配置
        self.load_config()
        
        # 创建界面
        self.create_widgets()
        
        # 设置日志
        self.setup_logging()
    
    def configure_styles(self):
        """配置UI样式"""
        style = ttk.Style()
        
        # 主题设置
        style.theme_use('clam')
        
        # 通用样式
        style.configure('.', background=self.bg_color, foreground=self.text_color)
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        style.configure('TButton', background=self.primary_color, foreground='white', 
                       font=('Microsoft YaHei', 10), padding=5)
        style.map('TButton', 
                  background=[('active', self.highlight_color), ('pressed', self.highlight_color)],
                  foreground=[('active', 'white'), ('pressed', 'white')])
        
        # 输入框样式
        style.configure('TEntry', fieldbackground='white', foreground=self.text_color)
        
        # 标签页样式
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_color,
                       padding=[10, 5], font=('Microsoft YaHei', 10))
        style.map('TNotebook.Tab', 
                 background=[('selected', self.primary_color)],
                 foreground=[('selected', 'white')])
        
        # 树状视图样式
        style.configure('Treeview', background='white', foreground=self.text_color,
                       fieldbackground='white', rowheight=25)
        style.configure('Treeview.Heading', background=self.secondary_color, 
                       foreground='white', font=('Microsoft YaHei', 10, 'bold'))
        style.map('Treeview', background=[('selected', self.highlight_color)],
                 foreground=[('selected', 'white')])
        
        # 进度条样式
        style.configure('Horizontal.TProgressbar', background=self.primary_color,
                       troughcolor=self.bg_color, thickness=20)
        
        # 单选按钮样式
        style.configure('TRadiobutton', background=self.bg_color, foreground=self.text_color)
        
        # 文本框样式
        style.configure('Text', background='white', foreground=self.text_color,
                       insertbackground=self.primary_color)
    
    def create_widgets(self):
        """创建主界面"""
        # 创建notebook用于标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.create_collection_tab()
        self.create_data_tab()
        self.create_user_data_tab()
        self.create_analysis_tab()
        self.create_help_tab()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_status_bar(self):
        """创建底部状态栏"""
        status_frame = ttk.Frame(self.root, relief='sunken')
        status_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        self.status_label = ttk.Label(status_frame, text="就绪", anchor='w')
        self.status_label.pack(side='left', padx=10)
        
        self.progress = ttk.Progressbar(status_frame, length=300, mode='determinate')
        self.progress.pack(side='right', padx=10)
    
    def create_collection_tab(self):
        """创建数据采集标签页"""
        collection_frame = ttk.Frame(self.notebook)
        self.notebook.add(collection_frame, text='数据采集')
        
        # 主容器
        main_container = ttk.Frame(collection_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧设置面板
        settings_frame = ttk.LabelFrame(main_container, text='采集设置', padding=10)
        settings_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # 浏览器设置
        browser_frame = ttk.LabelFrame(settings_frame, text='浏览器设置', padding=5)
        browser_frame.pack(fill='x', padx=5, pady=5)
        
        path_frame = ttk.Frame(browser_frame)
        path_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(path_frame, text="Chrome路径:").pack(side='left', padx=5)
        path_entry = ttk.Entry(path_frame, textvariable=self.browser_path, width=40)
        path_entry.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(path_frame, text="选择", command=self.select_browser_path).pack(side='left', padx=5)
        
        # 数据来源设置
        source_frame = ttk.LabelFrame(settings_frame, text='数据来源', padding=5)
        source_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(source_frame, text="抖音链接:").pack(anchor='w', padx=5, pady=2)
        ttk.Entry(source_frame, textvariable=self.url, width=40).pack(fill='x', padx=5, pady=2)
        
        # 搜索设置
        search_frame = ttk.LabelFrame(settings_frame, text='关键词搜索', padding=5)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索关键词:").pack(anchor='w', padx=5, pady=2)
        self.search_keyword = tk.StringVar(value="音乐")
        keyword_entry = ttk.Entry(search_frame, textvariable=self.search_keyword, width=40)
        keyword_entry.pack(fill='x', padx=5, pady=2)
        keyword_entry.bind('<Return>', lambda event: self.start_search_collection())
        
        # 搜索类型选择
        type_frame = ttk.Frame(search_frame)
        type_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(type_frame, text="搜索类型:").pack(side='left', padx=5)
        
        self.search_type = tk.StringVar(value='video')
        search_types = [('视频', 'video'), ('用户', 'user')]
        
        for text, value in search_types:
            ttk.Radiobutton(
                type_frame,
                text=text,
                value=value,
                variable=self.search_type
            ).pack(side='left', padx=10)
        
        # 采集参数设置
        param_frame = ttk.LabelFrame(settings_frame, text='采集参数', padding=5)
        param_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(param_frame, text="滚动次数:").pack(anchor='w', padx=5, pady=2)
        ttk.Entry(param_frame, textvariable=self.scroll_count, width=10).pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(param_frame, text="延迟(秒):").pack(anchor='w', padx=5, pady=2)
        ttk.Entry(param_frame, textvariable=self.delay, width=10).pack(anchor='w', padx=5, pady=2)
        
        # 操作按钮
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="搜索采集", command=self.start_search_collection).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(button_frame, text="停止采集", command=self.stop_collection).pack(side='left', padx=5, fill='x', expand=True)
        
        # 右侧预览面板
        preview_frame = ttk.LabelFrame(main_container, text='数据预览', padding=10)
        preview_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # 预览文本区域
        self.preview_text = tk.Text(preview_frame, height=20, width=60, wrap=tk.WORD)
        self.preview_text.pack(fill='both', expand=True, pady=5)
        
        # 预览控制按钮
        preview_btn_frame = ttk.Frame(preview_frame)
        preview_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(preview_btn_frame, text="清空预览", command=lambda: self.preview_text.delete(1.0, tk.END)).pack(side='left', padx=5)
        ttk.Button(preview_btn_frame, text="复制内容", command=self.copy_preview_content).pack(side='left', padx=5)
    
    def create_data_tab(self):
        """创建数据查看标签页"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text='数据查看')
        
        # 主容器
        container = ttk.Frame(data_frame)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 工具栏
        toolbar = ttk.Frame(container)
        toolbar.pack(fill='x', pady=5)
        
        # 添加导出按钮
        export_menu = tk.Menubutton(toolbar, text="导出数据", relief='raised')
        export_menu.pack(side='left', padx=5)
        
        export_menu.menu = tk.Menu(export_menu, tearoff=0)
        export_menu["menu"] = export_menu.menu
        export_menu.menu.add_command(label="导出Excel", command=self.export_excel)
        export_menu.menu.add_command(label="导出JSON", command=self.export_json)
        
        # 添加统计标签
        self.stats_label = ttk.Label(toolbar, text="共采集到 0 条数据")
        self.stats_label.pack(side='right', padx=5)
        
        # 创建表格
        columns = ('序号', '标题', '作者', '发布时间', '点赞数', '视频链接')
        self.data_tree = ttk.Treeview(container, columns=columns, show='headings', selectmode='extended')
        
        # 设置列标题和宽度
        for col in columns:
            self.data_tree.heading(col, text=col, command=lambda c=col: self.treeview_sort_column(self.data_tree, c, False))
        
        # 设置列宽
        self.data_tree.column('序号', width=50, anchor='center')
        self.data_tree.column('标题', width=200)
        self.data_tree.column('作者', width=100)
        self.data_tree.column('发布时间', width=100)
        self.data_tree.column('点赞数', width=70, anchor='center')
        self.data_tree.column('视频链接', width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scrollbar.set)
        
        # 使用grid布局管理器
        self.data_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定双击事件
        self.data_tree.bind('<Double-1>', self.on_tree_double_click)
        
        # 绑定右键菜单事件
        self.data_tree.bind('<Button-3>', self.show_video_context_menu)
        
        # 创建右键菜单
        self.video_menu = tk.Menu(self.root, tearoff=0)
        self.video_menu.add_command(label="复制视频链接", command=self.copy_video_link)
        self.video_menu.add_command(label="在浏览器中打开", command=self.open_in_browser)
        self.video_menu.add_separator()
        self.video_menu.add_command(label="查看详情", command=self.show_video_details)
    
    def create_user_data_tab(self):
        """创建用户数据查看标签页"""
        user_frame = ttk.Frame(self.notebook)
        self.notebook.add(user_frame, text='用户数据')
        
        # 主容器
        container = ttk.Frame(user_frame)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 工具栏
        toolbar = ttk.Frame(container)
        toolbar.pack(fill='x', pady=5)
        
        # 添加导出按钮
        export_menu = tk.Menubutton(toolbar, text="导出数据", relief='raised')
        export_menu.pack(side='left', padx=5)
        
        export_menu.menu = tk.Menu(export_menu, tearoff=0)
        export_menu["menu"] = export_menu.menu
        export_menu.menu.add_command(label="导出Excel", command=self.export_user_excel)
        export_menu.menu.add_command(label="导出JSON", command=self.export_user_json)
        
        # 添加统计标签
        self.user_stats_label = ttk.Label(toolbar, text="共采集到 0 位用户")
        self.user_stats_label.pack(side='right', padx=5)
        
        # 创建表格
        columns = ('序号', '用户名', '抖音号', '获赞数', '粉丝数', '简介', '主页链接', '头像链接')
        self.user_tree = ttk.Treeview(container, columns=columns, show='headings', selectmode='extended')
        
        # 设置列标题和排序功能
        for col in columns:
            self.user_tree.heading(col, text=col, command=lambda c=col: self.treeview_sort_column(self.user_tree, c, False))
        
        # 设置列宽
        self.user_tree.column('序号', width=50, anchor='center')
        self.user_tree.column('用户名', width=150)
        self.user_tree.column('抖音号', width=100)
        self.user_tree.column('获赞数', width=70, anchor='center')
        self.user_tree.column('粉丝数', width=70, anchor='center')
        self.user_tree.column('简介', width=200)
        self.user_tree.column('主页链接', width=150)
        self.user_tree.column('头像链接', width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.user_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定双击事件
        self.user_tree.bind('<Double-1>', self.on_user_tree_double_click)
        
        # 绑定右键菜单事件
        self.user_tree.bind('<Button-3>', self.show_user_context_menu)
        
        # 创建右键菜单
        self.user_menu = tk.Menu(self.root, tearoff=0)
        self.user_menu.add_command(label="复制主页链接", command=self.copy_user_link)
        self.user_menu.add_command(label="在浏览器中打开", command=self.open_user_in_browser)
        self.user_menu.add_separator()
        self.user_menu.add_command(label="查看详情", command=self.show_user_details)
    
    def create_analysis_tab(self):
        """创建数据分析标签页"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text='数据分析')
        
        # 主容器
        container = ttk.Frame(analysis_frame)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 分析选项面板
        options_frame = ttk.LabelFrame(container, text='分析选项', padding=10)
        options_frame.pack(fill='x', padx=5, pady=5)
        
        # 分析按钮
        btn_frame = ttk.Frame(options_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="互动数据分析", command=self.analyze_interaction_data).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(btn_frame, text="内容长度分析", command=self.analyze_content_length).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(btn_frame, text="高频词汇分析", command=self.analyze_keywords).pack(side='left', padx=5, fill='x', expand=True)
        
        # 图表类型选择
        chart_frame = ttk.Frame(options_frame)
        chart_frame.pack(fill='x', pady=5)
        
        ttk.Label(chart_frame, text="图表类型:").pack(side='left', padx=5)
        self.chart_type = tk.StringVar(value='bar')
        
        chart_types = [('柱状图', 'bar'), ('折线图', 'line'), ('饼图', 'pie')]
        for text, value in chart_types:
            ttk.Radiobutton(
                chart_frame,
                text=text,
                value=value,
                variable=self.chart_type
            ).pack(side='left', padx=5)
        
        # 分析结果区域
        result_frame = ttk.LabelFrame(container, text='分析结果', padding=10)
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建分析结果文本框
        self.analysis_text = tk.Text(result_frame, wrap=tk.WORD, padx=10, pady=10)
        self.analysis_text.pack(fill='both', expand=True, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.analysis_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.analysis_text.configure(yscrollcommand=scrollbar.set)
        
        # 结果操作按钮
        result_btn_frame = ttk.Frame(result_frame)
        result_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(result_btn_frame, text="清空分析结果", command=lambda: self.analysis_text.delete(1.0, tk.END)).pack(side='left', padx=5)
        ttk.Button(result_btn_frame, text="复制结果", command=self.copy_analysis_result).pack(side='left', padx=5)
        ttk.Button(result_btn_frame, text="保存结果", command=self.save_analysis_result).pack(side='left', padx=5)
    
    def create_help_tab(self):
        """创建帮助标签页"""
        help_frame = ttk.Frame(self.notebook)
        self.notebook.add(help_frame, text='使用帮助')
        
        # 主容器
        container = ttk.Frame(help_frame)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建帮助文本框
        help_text = tk.Text(container, wrap=tk.WORD, padx=15, pady=15)
        help_text.pack(fill='both', expand=True)
        
        # 添加标签用于样式化文本
        help_text.tag_configure('title', font=('Microsoft YaHei', 14, 'bold'), foreground=self.primary_color)
        help_text.tag_configure('subtitle', font=('Microsoft YaHei', 12, 'bold'), foreground=self.secondary_color)
        help_text.tag_configure('highlight', foreground=self.highlight_color)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=help_text.yview)
        scrollbar.pack(side='right', fill='y')
        help_text.configure(yscrollcommand=scrollbar.set)
        
        # 帮助内容
        help_content = [
            ("抖音作品分析工具使用指南\n", 'title'),
            ("\n1. 数据采集\n", 'subtitle'),
            ("支持两种采集方式：\n- 直接输入抖音链接\n- 关键词搜索采集\n\n", None),
            ("关键词搜索支持以下类型：\n- 视频搜索\n- 用户搜索\n\n", None),
            ("采集参数说明：\n- 滚动次数：决定采集数据量的多少\n- 延迟(秒)：每次滚动的等待时间，建议2-3秒\n\n", None),
            ("使用技巧：\n", 'highlight'),
            ("- 采集时可随时点击停止采集\n- 建议设置适当的延迟避免被限制\n- 数据采集过程中请勿关闭浏览器窗口\n\n", None),
            ("\n2. 数据查看\n", 'subtitle'),
            ("视频数据：\n- 包含标题、作者、发布时间等信息\n- 双击可直接打开视频链接\n- 支持按列排序\n- 可导出为Excel或JSON格式\n\n", None),
            ("用户数据：\n- 显示用户名、抖音号、粉丝数等信息\n- 双击可打开用户主页\n- 支持数据排序\n- 可单独导出用户数据\n\n", None),
            ("\n3. 数据分析\n", 'subtitle'),
            ("互动数据分析：\n- 统计总点赞数、平均点赞等指标\n- 展示互动数据分布情况\n\n", None),
            ("内容长度分析：\n- 分析标题长度分布\n- 显示最长/最短标题统计\n\n", None),
            ("高频词汇分析：\n- 提取标题中的关键词\n- 展示TOP100高频词汇\n- 计算词频占比\n\n", None),
            ("\n4. 常见问题\n", 'subtitle'),
            ("Q: 为什么采集速度较慢？\nA: 为了避免被反爬虫机制拦截，程序设置了延迟机制。\n\n", None),
            ("Q: 如何提高采集成功率？\nA: 建议：\n- 设置适当的延迟时间（2-3秒）\n- 避免过于频繁的采集\n- 确保网络连接稳定\n\n", None),
            ("Q: 数据导出格式说明？\nA: 支持两种格式：\n- Excel格式：适合数据分析和处理\n- JSON格式：适合数据备份和程序读取\n\n", None),
            ("Q: 如何处理采集失败？\nA: 可以：\n- 检查网络连接\n- 增加延迟时间\n- 减少单次采集数量\n- 更换搜索关键词\n\n", None),
            ("\n5. 注意事项\n", 'subtitle'),
            ("合理使用：\n- 遵守抖音平台规则\n- 避免频繁、大量采集\n- 合理设置采集参数\n\n", None),
            ("数据安全：\n- 及时导出重要数据\n- 定期备份采集结果\n\n", None),
            ("使用建议：\n- 建议使用稳定的网络连接\n- 采集时避免其他浏览器操作\n- 定期清理浏览器缓存\n", None)
        ]
        
        # 插入帮助内容
        for text, tag in help_content:
            if tag:
                help_text.insert('end', text, tag)
            else:
                help_text.insert('end', text)
        
        help_text.config(state='disabled')  # 设置为只读
    
    # ====================== 以下是原有功能方法 ======================
    # 由于篇幅限制，这里只展示UI优化部分，原有功能方法保持不变
    # 请将原始代码中的功能方法复制到这里，保持完整功能
    
    def setup_logging(self):
        """设置日志"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"douyin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def copy_preview_content(self):
        """复制预览内容到剪贴板"""
        content = self.preview_text.get(1.0, tk.END)
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("成功", "预览内容已复制到剪贴板")
    
    def copy_analysis_result(self):
        """复制分析结果到剪贴板"""
        content = self.analysis_text.get(1.0, tk.END)
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("成功", "分析结果已复制到剪贴板")
    
    def save_analysis_result(self):
        """保存分析结果到文件"""
        content = self.analysis_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("警告", "没有可保存的分析结果！")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"分析结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"分析结果已保存到:\n{filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    
    def show_video_details(self):
        """显示视频详情"""
        selection = self.data_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.data_tree.item(item)['values']
        if not values:
            return
        
        details = f"视频详情:\n\n标题: {values[1]}\n作者: {values[2]}\n发布时间: {values[3]}\n点赞数: {values[4]}\n链接: {values[5]}"
        messagebox.showinfo("视频详情", details)
    
    def show_user_details(self):
        """显示用户详情"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.user_tree.item(item)['values']
        if not values:
            return
        
        details = f"用户详情:\n\n用户名: {values[1]}\n抖音号: {values[2]}\n获赞数: {values[3]}\n粉丝数: {values[4]}\n简介: {values[5]}\n主页链接: {values[6]}"
        messagebox.showinfo("用户详情", details)
    
    def show_user_context_menu(self, event):
        """显示用户右键菜单"""
        try:
            item = self.user_tree.identify_row(event.y)
            if not item:
                return
            
            self.user_tree.selection_set(item)
            self.user_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"显示用户右键菜单错误: {str(e)}")
    
    def copy_user_link(self):
        """复制用户链接到剪贴板"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.user_tree.item(item)['values']
        if not values:
            return
        
        user_url = values[6]
        if user_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(user_url)
            messagebox.showinfo("成功", "用户主页链接已复制到剪贴板")
    
    def open_user_in_browser(self):
        """在浏览器中打开用户主页"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.user_tree.item(item)['values']
        if not values:
            return
        
        user_url = values[6]
        if user_url:
            if not user_url.startswith('http'):
                if user_url.startswith('//'):
                    user_url = 'https:' + user_url
                else:
                    user_url = 'https://www.douyin.com' + user_url
            
            webbrowser.open(user_url)

    def on_tree_double_click(self, event):
        """处理表格双击事件"""
        try:
            item = self.data_tree.selection()[0]
            values = self.data_tree.item(item)['values']
            if not values:
                return
                 
            video_url = values[5]  # 获取视频链接
            if video_url:
                # 确保URL格式正确
                if not video_url.startswith('http'):
                    if video_url.startswith('//'):
                        video_url = 'https:' + video_url
                    elif video_url.startswith('/'):
                        video_url = 'https://www.douyin.com' + video_url
                    else:
                        video_url = 'https://www.douyin.com/' + video_url
                 
                # 使用默认浏览器打开链接
                import webbrowser
                webbrowser.open(video_url)
                 
        except Exception as e:
            print(f"打开视频链接错误: {str(e)}")
            messagebox.showerror("错误", "无法打开视频链接")
 
    def on_user_tree_double_click(self, event):
        """处理用户表格双击事件"""
        try:
            item = self.user_tree.selection()[0]
            values = self.user_tree.item(item)['values']
            if not values:
                return
             
            user_url = values[6]  # 获取用户主页链接
            if user_url:
                # 确保URL格式正确
                if not user_url.startswith('http'):
                    if user_url.startswith('//'):
                        user_url = 'https:' + user_url
                    elif user_url.startswith('/'):
                        user_url = 'https://www.douyin.com' + user_url
                    else:
                        user_url = 'https://www.douyin.com/' + user_url
                 
                # 使用默认浏览器打开链接
                import webbrowser
                webbrowser.open(user_url)
             
        except Exception as e:
            print(f"打开用户主页链接错误: {str(e)}")
            messagebox.showerror("错误", "无法打开用户主页链接")
 
    def create_analysis_tab(self):
        """创建数据分析标签页"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text='数据分析')
         
        # 创建分析结果文本框
        self.analysis_text = tk.Text(analysis_frame, height=20, width=60)
        self.analysis_text.pack(pady=10, padx=10, fill='both', expand=True)
         
        # 创建按钮框架
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(pady=5)
         
        # 添加分析按钮
        ttk.Button(button_frame, text="互动数据分析", command=self.analyze_interaction_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="内容长度分析", command=self.analyze_content_length).pack(side='left', padx=5)
        ttk.Button(button_frame, text="高频词汇分析", command=self.analyze_keywords).pack(side='left', padx=5)
        ttk.Button(button_frame, text="清空分析结果", command=lambda: self.analysis_text.delete(1.0, tk.END)).pack(side='left', padx=5)
     
    def start_search_collection(self):
        """开始搜索采集"""
        try:
            # 验证输入
            keyword = self.search_keyword.get().strip()
            if not keyword:
                messagebox.showwarning("警告", "请输入搜索关键词！")
                return
             
            scroll_count = self.scroll_count.get().strip()
            if not scroll_count.isdigit():
                messagebox.showwarning("警告", "滚动次数必须是正整数！")
                return
             
            delay = self.delay.get().strip()
            try:
                delay = float(delay)
                if delay <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("警告", "延迟时间必须是正数！")
                return
             
            # 检查是否已经在运行
            if self.is_running:
                messagebox.showwarning("警告", "采集正在进行中！")
                return
             
            # 清空之前的数据
            self.collected_data = []
            self.update_data_display()
             
            # 更新状态
            self.status_label.config(text="正在启动采集...")
            self.progress['value'] = 0
             
            # 启动采集线程
            self.is_running = True
            threading.Thread(target=self.scroll_and_collect_search, daemon=True).start()
             
        except Exception as e:
            self.is_running = False
            error_msg = f"启动采集失败: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            messagebox.showerror("错误", error_msg)
 
    def init_browser(self):
        """初始化浏览器"""
        try:
            if self.page is None:
                from DrissionPage import ChromiumPage
                 
                # 直接创建页面对象，使用最简单的方式
                self.page = ChromiumPage()
                 
                # 如果需要设置浏览器路径，可以使用这种方式
                # self.page.set.browser_path = self.browser_path.get()
                 
                time.sleep(2)  # 等待浏览器启动
                return True
                 
            return True
             
        except Exception as e:
            print(f"初始化浏览器失败: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("错误", f"初始化浏览器失败: {str(e)}\n请检查Chrome浏览器路径是否正确")
            return False
 
    def scroll_and_collect_search(self):
        """滚动页面并收集搜索结果数据"""
        if not self.init_browser():
            return
             
        try:
            # 构建搜索URL
            keyword = self.search_keyword.get().strip()
            search_type = self.search_type.get()
            search_url = f"https://www.douyin.com/search/{quote(keyword)}?source=normal_search&type={search_type}"
            print(f"访问搜索URL: {search_url}")
             
            # 访问页面
            self.page.get(search_url)
            time.sleep(5)  # 增加等待时间
             
            # 直接开始采集
            print("开始采集...")
             
            # 获取滚动次数和延迟
            scroll_times = int(self.scroll_count.get())
            delay = float(self.delay.get())
             
            # 开始滚动和采集
            last_height = self.page.run_js("return document.body.scrollHeight")
             
            for i in range(scroll_times):
                if not self.is_running:
                    break
                 
                try:
                    # 滚动页面
                    self.page.run_js("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(delay)
                     
                    # 检查是否到达底部
                    new_height = self.page.run_js("return document.body.scrollHeight")
                    if new_height == last_height:
                        print("已到达页面底部")
                        break
                    last_height = new_height
                     
                    # 获取页面源码并解析
                    page_source = self.page.html
                    soup = BeautifulSoup(page_source, 'html.parser')
                     
                    # 根据搜索类型选择不同的提取方法
                    if search_type == 'user':
                        new_data = self.extract_user_data(soup)
                    else:
                        container = soup.select_one('[data-e2e="scroll-list"]')
                        if container:
                            new_data = self.extract_video_items(container)
                        else:
                            print("未找到视频列表容器")
                            continue
                     
                    print(f"本次滚动找到 {len(new_data)} 条新数据")
                     
                    # 添加新数据（去重）
                    for data in new_data:
                        if data not in self.collected_data:
                            self.collected_data.append(data)
                     
                    print(f"当前总共采集 {len(self.collected_data)} 条数据")
                     
                    # 更新数据显示
                    self.root.after(0, self.update_data_display)
                     
                    # 更新状态
                    self.root.after(0, lambda: self.status_label.config(text=f"正在滚动... ({i+1}/{scroll_times})"))
                    self.root.after(0, lambda: self.progress.configure(value=((i + 1) / scroll_times * 100)))
                     
                except Exception as e:
                    print(f"滚动错误: {str(e)}")
                    continue
             
            print("搜索结果采集完成")
            self.root.after(0, lambda: self.status_label.config(text=f"采集完成，共获取{len(self.collected_data)}条数据"))
             
        except Exception as e:
            error_msg = f"采集过程出错: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
             
        finally:
            self.is_running = False
            if self.page:
                self.page.quit()  # 关闭浏览器
 
    def extract_video_data(self, html):
        """提取数据"""
        if self.search_type.get() == 'user':
            return self.extract_user_data(html)
        else:
            return self.extract_video_items(html)
 
    def extract_user_data(self, html):
        """提取用户数据"""
        print("开始提取用户数据...")
         
        # 使用正确的选择器定位用户列表
        user_items = html.select("div.search-result-card > a.hY8lWHgA.poLTDMYS")  # 更新选择器
        print(f"找到 {len(user_items)} 个用户项")
         
        user_data = []
         
        for item in user_items:
            try:
                # 获取用户链接
                user_link = item.get('href', '')
                 
                # 获取标题
                title_elem = item.select_one('div.XQwChAbX p.v9LWb7QE span span span span span')
                title = title_elem.get_text(strip=True) if title_elem else ''
                 
                # 获取头像URL
                avatar_elem = item.select_one('img.RlLOO79h')
                avatar_url = avatar_elem.get('src', '') if avatar_elem else ''
                 
                # 获取统计数据
                stats_div = item.select_one('div.jjebLXt0')
                douyin_id = ''
                likes = '0'
                followers = '0'
                 
                if stats_div:
                    spans = stats_div.select('span')
                    for span in spans:
                        text = span.get_text(strip=True)
                        print(f"处理span文本: {text}")  # 调试输出
                         
                        if '抖音号:' in text or '抖音号：' in text:
                            id_span = span.select_one('span')
                            if id_span:
                                douyin_id = id_span.get_text(strip=True)
                        elif '获赞' in text:
                            likes = text.replace('获赞', '').strip()
                        elif '粉丝' in text:
                            followers = text.replace('粉丝', '').strip()
                 
                # 获取简介
                desc_elem = item.select_one('p.Kdb5Km3i span span span span span')
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                 
                # 构建数据
                data = {
                    'title': title,
                    'douyin_id': douyin_id,
                    'likes': likes,
                    'followers': followers,
                    'description': description,
                    'avatar_url': avatar_url,
                    'user_link': user_link
                }
                 
                # 清理数据
                data = {k: self.clean_text(str(v)) for k, v in data.items()}
                 
                # 格式化数字
                data['likes'] = self.format_number(data['likes'])
                data['followers'] = self.format_number(data['followers'])
                 
                # 处理用户链接
                if data['user_link'] and not data['user_link'].startswith('http'):
                    data['user_link'] = 'https://www.douyin.com' + data['user_link']
                 
                # 打印调试信息
                print("\n提取到的数据:")
                for key, value in data.items():
                    print(f"{key}: {value}")
                 
                # 只要有标题就添加
                if data['title']:
                    if data not in user_data:  # 确保不重复添加
                        user_data.append(data)
                        print(f"成功提取用户数据: {data['title']}")
                 
            except Exception as e:
                print(f"提取单个用户数据错误: {str(e)}")
                traceback.print_exc()  # 打印完整的错误堆栈
                continue
         
        print(f"总共提取到 {len(user_data)} 条用户数据")
        return user_data
 
    def _extract_basic_info(self, item):
        """提取基本信息"""
        # 获取用户链接
        user_link = item.select_one('a.uz1VJwFY')  # 使用确切的类名
         
        # 获取标题
        title = ""
        title_elem = item.select_one('p.ZMZLqKYm span')  # 使用确切的类名和结构
        if title_elem:
            title = title_elem.get_text(strip=True)
         
        # 获取头像URL
        avatar_elem = item.select_one('img.fiWP27dC')
        avatar_url = avatar_elem.get('src', '') if avatar_elem else ''
         
        return {
            'title': title,
            'douyin_id': '',
            'likes': '',
            'followers': '',
            'description': '',
            'avatar_url': avatar_url,
            'user_link': user_link.get('href', '') if user_link else ''
        }
 
    def _extract_stats_info(self, item, data):
        """提取统计信息"""
        stats_div = item.select_one('div.Y6iuJGlc')  # 使用确切的类名
         
        if stats_div:
            spans = stats_div.select('span')
            spans_text = [span.get_text(strip=True) for span in spans]
            print(f"找到的span文本: {spans_text}")  # 调试输出
             
            for text in spans_text:
                if '抖音号:' in text or '抖音号：' in text:
                    # 获取嵌套的span中的抖音号
                    nested_span = stats_div.select_one('span > span')
                    if nested_span:
                        data['douyin_id'] = nested_span.get_text(strip=True)
                elif '获赞' in text:
                    data['likes'] = text.replace('获赞', '').strip()
                elif '粉丝' in text:
                    data['followers'] = text.replace('粉丝', '').strip()
 
    def _extract_description(self, item, data):
        """提取用户简介"""
        desc_elem = item.select_one('p.NYqiIDUo span')  # 使用确切的类名和结构
        if desc_elem:
            # 获取纯文本内容，去除表情图片
            text_nodes = [node for node in desc_elem.stripped_strings]
            data['description'] = ' '.join(text_nodes)
 
    def _clean_and_format_data(self, data):
        """清理和格式化数据"""
        # 清理文本数据
        for key in data:
            if isinstance(data[key], str):
                data[key] = self.clean_text(data[key])
         
        # 格式化数字
        data['likes'] = self.format_number(data['likes'])
        data['followers'] = self.format_number(data['followers'])
         
        # 处理用户链接
        if data['user_link']:
            link = data['user_link']
            # 移除查询参数
            if '?' in link:
                link = link.split('?')[0]
            # 确保正确的格式
            if link.startswith('//'):
                link = 'https:' + link
            elif not link.startswith('http'):
                # 移除可能的重复路径
                link = link.replace('www.douyin.com/', '')
                link = link.replace('//', '/')
                if not link.startswith('/'):
                    link = '/' + link
                link = 'https://www.douyin.com' + link
             
            print(f"原始链接: {data['user_link']}")  # 调试输出
            print(f"处理后链接: {link}")  # 调试输出
            data['user_link'] = link
 
    def _print_debug_info(self, data):
        """打印调试信息"""
        print("\n提取到的数据:")
        print(f"标题: {data['title']}")
        print(f"抖音号: {data['douyin_id']}")
        print(f"获赞: {data['likes']}")
        print(f"粉丝: {data['followers']}")
        print(f"简介: {data['description'][:50]}...")
        print(f"链接: {data['user_link']}")
 
    def extract_video_items(self, html):
        """提取视频数据(原有代码)"""
        video_items = html.select("li.SwZLHMKk")
        video_data = []
         
        for item in video_items:
            try:
                # 获取视频链接
                video_link = item.select_one('a.hY8lWHgA')
                if not video_link:
                    continue
                 
                # 构建数据
                data = {
                    'video_url': video_link['href'].strip(),
                    'cover_image': item.select_one('img')['src'].strip() if item.select_one('img') else '',
                    'title': item.select_one('div.VDYK8Xd7').text.strip() if item.select_one('div.VDYK8Xd7') else '无标题',
                    'author': item.select_one('span.MZNczJmS').text.strip() if item.select_one('span.MZNczJmS') else '未知作者',
                    'publish_time': item.select_one('span.faDtinfi').text.strip() if item.select_one('span.faDtinfi') else '',
                    'likes': item.select_one('span.cIiU4Muu').text.strip() if item.select_one('span.cIiU4Muu') else '0'
                }
                 
                # 清理数据
                data = {k: self.clean_text(str(v)) for k, v in data.items()}
                 
                # 验证数据完整性
                if all(data.values()):
                    video_data.append(data)
                else:
                    print(f"跳过不完整数据: {data}")
                 
            except Exception as e:
                print(f"提取单个视频数据错误: {str(e)}")
                continue
         
        return video_data
 
    def update_data_display(self):
        """更新数据显示"""
        try:
            search_type = self.search_type.get()
            print(f"更新数据显示，搜索类型: {search_type}")
            print(f"当前数据数量: {len(self.collected_data)}")
             
            if search_type == 'user':
                self.notebook.select(2)  # 先切换到用户数据标签页
                self.root.after(100, self.update_user_display)  # 延迟一小段时间后更新显示
            else:
                self.notebook.select(1)  # 切换到视频数据标签页
                self.root.after(100, self.update_video_display)
             
        except Exception as e:
            print(f"更新数据显示错误: {str(e)}")
 
    def update_user_display(self):
        """更新用户数据显示"""
        try:
            # 清空现有显示
            self.user_tree.delete(*self.user_tree.get_children())
             
            # 添加新数据
            for i, data in enumerate(self.collected_data):
                try:
                    # 格式化简介
                    description = data.get('description', '')
                    if len(description) > 50:
                        description = description[:47] + '...'
                     
                    # 格式化数据
                    values = (
                        i + 1,
                        data.get('title', ''),
                        data.get('douyin_id', ''),
                        self.format_number(str(data.get('likes', '0'))),
                        self.format_number(str(data.get('followers', '0'))),
                        description,
                        data.get('user_link', ''),
                        data.get('avatar_url', '')
                    )
                     
                    self.user_tree.insert('', 'end', values=values)
                    print(f"显示用户数据: {data.get('title', '')}")
                     
                except Exception as e:
                    print(f"处理单条用户数据显示错误: {str(e)}")
                    continue
             
            # 更新统计
            self.user_stats_label.config(text=f"共采集到 {len(self.collected_data)} 位用户")
            print(f"更新用户统计: {len(self.collected_data)} 位用户")
             
            # 自动滚动到最新数据
            if self.user_tree.get_children():
                self.user_tree.see(self.user_tree.get_children()[-1])
             
        except Exception as e:
            print(f"更新用户数据显示错误: {str(e)}")
 
    def update_video_display(self):
        """更新视频数据显示(原有的update_data_display逻辑)"""
        try:
            # 清空现有显示
            self.data_tree.delete(*self.data_tree.get_children())
             
            # 添加新数据
            for i, data in enumerate(self.collected_data):
                try:
                    title = data.get('title', '')
                    if len(title) > 50:
                        title = title[:47] + '...'
                     
                    values = (
                        i + 1,
                        title,
                        data.get('author', '未知作者'),
                        data.get('publish_time', ''),
                        self.format_number(str(data.get('likes', '0'))),
                        data.get('video_url', '')
                    )
                     
                    self.data_tree.insert('', 'end', values=values)
                     
                except Exception as e:
                    print(f"处理单条数据显示错误: {str(e)}")
                    continue
             
            # 更新统计
            self.stats_label.config(text=f"共采集到 {len(self.collected_data)} 条数据")
             
            # 自动滚动到最新数据
            if self.data_tree.get_children():
                self.data_tree.see(self.data_tree.get_children()[-1])
             
        except Exception as e:
            print(f"更新数据显示错误: {str(e)}")
 
    def update_data_stats(self):
        """更新数据统计"""
        try:
            total_count = len(self.collected_data)
            self.stats_label.config(text=f"共采集到 {total_count} 条数据")
        except Exception as e:
            print(f"更新统计信息错误: {str(e)}")
 
    def stop_collection(self):
        """停止数据采集"""
        if self.is_running:
            self.is_running = False
            self.status_label.config(text="已停止采集")
            print("采集已停止")
        else:
            print("当前没有正在进行的采集任务")
 
    def export_excel(self):
        """导出数据到Excel"""
        if not self.collected_data:
            messagebox.showwarning("警告", "没有数据可导出！")
            return
             
        try:
            filename = f"抖音数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df = pd.DataFrame(self.collected_data)
            df.to_excel(filename, index=False)
            messagebox.showinfo("成功", f"数据已导出到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出Excel失败: {str(e)}")
 
    def export_json(self):
        """导出数据到JSON"""
        if not self.collected_data:
            messagebox.showwarning("警告", "没有数据可导出！")
            return
             
        try:
            filename = f"抖音数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"数据已导出到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出JSON失败: {str(e)}")
 
    def export_user_excel(self):
        """导出用户数据到Excel"""
        if not self.collected_data or self.search_type.get() != 'user':
            messagebox.showwarning("警告", "没有用户数据可导出！")
            return
         
        try:
            filename = f"抖音用户数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df = pd.DataFrame(self.collected_data)
            df.to_excel(filename, index=False)
            messagebox.showinfo("成功", f"用户数据已导出到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出Excel失败: {str(e)}")
 
    def export_user_json(self):
        """导出用户数据到JSON"""
        if not self.collected_data or self.search_type.get() != 'user':
            messagebox.showwarning("警告", "没有用户数据可导出！")
            return
         
        try:
            filename = f"抖音用户数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"用户数据已导出到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出JSON失败: {str(e)}")
 
    def clean_text(self, text):
        """清理文本"""
        return text.replace('\n', ' ').replace('\r', '').strip()
 
    def format_number(self, num_str):
        """格式化数字字符串"""
        try:
            num = int(num_str)
            if num >= 10000:
                return f"{num / 10000:.1f}万"
            return str(num)
        except ValueError:
            return num_str
 
    def analyze_interaction_data(self):
        """分析互动数据"""
        if not self.collected_data:
            messagebox.showwarning("警告", "没有可分析的数据！")
            return
         
        try:
            # 将点赞数转换为数字
            likes_data = []
            for data in self.collected_data:
                likes = str(data['likes'])
                try:
                    if '万' in likes:
                        # 处理带"万"的数字
                        num = float(likes.replace('万', '')) * 10000
                        likes_data.append(int(num))
                    else:
                        # 处理普通数字
                        likes_data.append(int(likes))
                except (ValueError, TypeError):
                    print(f"无法解析的点赞数: {likes}")
                    continue
             
            # 计算统计数据
            total_likes = sum(likes_data)
            avg_likes = total_likes / len(likes_data) if likes_data else 0
            max_likes = max(likes_data) if likes_data else 0
             
            # 生成报告
            report = "===== 互动数据分析报告 =====\n\n"
            report += f"总视频数: {len(self.collected_data)}\n"
            report += f"总点赞数: {self.format_large_number(total_likes)}\n"
            report += f"平均点赞数: {self.format_large_number(int(avg_likes))}\n"
            report += f"最高点赞数: {self.format_large_number(max_likes)}\n"
             
            # 显示分析结果
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, report)
             
        except Exception as e:
            print(f"互动数据分析错误: {str(e)}")
            messagebox.showerror("错误", f"分析失败: {str(e)}")
 
    def format_large_number(self, num):
        """格式化大数字显示"""
        if num >= 10000:
            return f"{num/10000:.1f}万"
        return str(num)
 
    def analyze_content_length(self):
        """分析内容长度"""
        if not self.collected_data:
            messagebox.showwarning("警告", "没有可分析的数据！")
            return
         
        try:
            # 计算标题长度
            title_lengths = [len(data['title']) for data in self.collected_data]
             
            # 计算统计数据
            avg_length = sum(title_lengths) / len(title_lengths)
            max_length = max(title_lengths)
            min_length = min(title_lengths)
             
            # 生成报告
            report = "===== 内容长度分析报告 =====\n\n"
            report += f"平均标题长度: {avg_length:.1f}字\n"
            report += f"最长标题: {max_length}字\n"
            report += f"最短标题: {min_length}字\n\n"
             
            # 添加长度分布统计
            length_ranges = [(0, 10), (11, 20), (21, 30), (31, 50), (51, 100), (101, float('inf'))]
            report += "标题长度分布:\n"
            for start, end in length_ranges:
                count = sum(1 for length in title_lengths if start <= length <= end)
                range_text = f"{start}-{end}字" if end != float('inf') else f"{start}字以上"
                percentage = (count / len(title_lengths)) * 100
                report += f"{range_text}: {count}个 ({percentage:.1f}%)\n"
             
            # 显示分析结果
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, report)
             
        except Exception as e:
            messagebox.showerror("错误", f"分析失败: {str(e)}")
 
    def analyze_keywords(self):
        """分析标题中的高频词汇"""
        if not self.collected_data:
            messagebox.showwarning("警告", "没有可分析的数据！")
            return
         
        try:
            # 合并所有标题文本
            all_titles = ' '.join(data['title'] for data in self.collected_data)
             
            # 设置停用词
            stop_words = {
                '的', '了', '是', '在', '我', '有', '和', '就',
                '都', '而', '及', '与', '着', '或', '等', '为',
                '一个', '没有', '这个', '那个', '但是', '而且',
                '只是', '不过', '这样', '一样', '一直', '一些',
                '这', '那', '也', '你', '我们', '他们', '它们',
                '把', '被', '让', '向', '往', '但', '去', '又',
                '能', '好', '给', '到', '看', '想', '要', '会',
                '多', '能', '这些', '那些', '什么', '怎么', '如何',
                '为什么', '可以', '因为', '所以', '应该', '可能', '应该'
            }
             
            # 使用jieba进行分词
            words = []
            for word in jieba.cut(all_titles):
                if len(word) > 1 and word not in stop_words:  # 过滤单字词和停用词
                    words.append(word)
             
            # 统计词频
            word_counts = Counter(words)
             
            # 生成报告
            report = "===== 高频词汇分析报告 =====\n\n"
            report += f"总标题数: {len(self.collected_data)}\n"
            report += f"总词汇量: {len(words)}\n"
            report += f"不同词汇数: {len(word_counts)}\n\n"
             
            # 显示高频词汇（TOP 100）
            report += "高频词汇 TOP 100:\n"
            report += "-" * 40 + "\n"
            report += "排名\t词汇\t\t出现次数\t频率\n"
            report += "-" * 40 + "\n"
             
            for rank, (word, count) in enumerate(word_counts.most_common(100), 1):
                frequency = (count / len(words)) * 100
                report += f"{rank}\t{word}\t\t{count}\t\t{frequency:.2f}%\n"
             
            # 显示分析结果
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, report)
             
        except Exception as e:
            print(f"高频词汇分析错误: {str(e)}")
            messagebox.showerror("错误", f"分析失败: {str(e)}")
 
    def treeview_sort_column(self, tree, col, reverse):
        """列排序函数"""
        # 获取所有项目
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
         
        try:
            # 尝试将数值型数据转换为数字进行排序
            if col in ['序号', '获赞数', '粉丝数', '点赞数']:
                # 处理带"万"的数字
                def convert_number(x):
                    try:
                        if '万' in x[0]:
                            return float(x[0].replace('万', '')) * 10000
                        return float(x[0])
                    except ValueError:
                        return 0
                 
                l.sort(key=convert_number, reverse=reverse)
            else:
                # 字符串排序
                l.sort(reverse=reverse)
        except Exception as e:
            print(f"排序错误: {str(e)}")
            # 如果转换失败，按字符串排序
            l.sort(reverse=reverse)
         
        # 重新排列项目
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)
            # 更新序号
            tree.set(k, '序号', str(index + 1))
         
        # 切换排序方向
        tree.heading(col, command=lambda: self.treeview_sort_column(tree, col, not reverse))
 
    def create_help_tab(self):
        """创建帮助标签页"""
        help_frame = ttk.Frame(self.notebook)
        self.notebook.add(help_frame, text='使用帮助')
         
        # 创建帮助文本框
        help_text = tk.Text(help_frame, wrap=tk.WORD, padx=10, pady=10)
        help_text.pack(fill='both', expand=True)
         
        # 添加滚动条
        scrollbar = ttk.Scrollbar(help_frame, orient='vertical', command=help_text.yview)
        scrollbar.pack(side='right', fill='y')
        help_text.configure(yscrollcommand=scrollbar.set)
         
        # 帮助内容
        help_content = """
抖音作品分析工具使用指南
====================
 
1. 数据采集
-----------------
 支持两种采集方式：
  - 直接输入抖音链接
  - 关键词搜索采集
 
 关键词搜索支持以下类型：
  - 视频搜索
  - 用户搜索
 
 采集参数说明：
  - 滚动次数：决定采集数据量的多少
  - 延迟(秒)：每次滚动的等待时间，建议2-3秒
 
 使用技巧：
  - 采集时可随时点击"停止采集"
  - 建议设置适当的延迟避免被限制
  - 数据采集过程中请勿关闭浏览器窗口
 
2. 数据查看
-----------------
 视频数据：
  - 包含标题、作者、发布时间等信息
  - 双击可直接打开视频链接
  - 支持按列排序
  - 可导出为Excel或JSON格式
 
 用户数据：
  - 显示用户名、抖音号、粉丝数等信息
  - 双击可打开用户主页
  - 支持数据排序
  - 可单独导出用户数据
 
3. 数据分析
-----------------
 互动数据分析：
  - 统计总点赞数、平均点赞等指标
  - 展示互动数据分布情况
 
 内容长度分析：
  - 分析标题长度分布
  - 显示最长/最短标题统计
 
 高频词汇分析：
  - 提取标题中的关键词
  - 展示TOP100高频词汇
  - 计算词频占比
 
4. 常见问题
-----------------
Q: 为什么采集速度较慢？
A: 为了避免被反爬虫机制拦截，程序设置了延迟机制。
 
Q: 如何提高采集成功率？
A: 建议：
   - 设置适当的延迟时间（2-3秒）
   - 避免过于频繁的采集
   - 确保网络连接稳定
 
Q: 数据导出格式说明？
A: 支持两种格式：
   - Excel格式：适合数据分析和处理
   - JSON格式：适合数据备份和程序读取
 
Q: 如何处理采集失败？
A: 可以：
   - 检查网络连接
   - 增加延迟时间
   - 减少单次采集数量
   - 更换搜索关键词
 
5. 注意事项
-----------------
 合理使用：
  - 遵守抖音平台规则
  - 避免频繁、大量采集
  - 合理设置采集参数
 
 数据安全：
  - 及时导出重要数据
  - 定期备份采集结果
 
 使用建议：
  - 建议使用稳定的网络连接
  - 采集时避免其他浏览器操作
  - 定期清理浏览器缓存
 
如需更多帮助，请参考项目文档或联系开发者。
"""
         
        # 插入帮助内容
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')  # 设置为只读
 
    def formatDouyinAwemeData(self, item):
        """格式化抖音视频数据"""
        video_data = {
            "awemeId": item.get("aweme_id"),
            "desc": item.get("desc", ""),
            "url": item.get("video", {}).get("play_addr", {}).get("url_list", [""])[0]  # 获取视频播放地址
        }
        return video_data
 
    def show_video_context_menu(self, event):
        """显示视频右键菜单"""
        try:
            # 获取点击的item
            item = self.data_tree.identify_row(event.y)
            if not item:
                return
             
            # 选中被点击的项
            self.data_tree.selection_set(item)
             
            # 显示菜单
            self.video_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"显示右键菜单错误: {str(e)}")
 
    def copy_video_link(self):
        """复制视频链接到剪贴板"""
        try:
            selection = self.data_tree.selection()
            if not selection:
                return
             
            item = selection[0]
            values = self.data_tree.item(item)['values']
            if not values:
                return
             
            video_url = values[5]
            if video_url:
                self.root.clipboard_clear()
                self.root.clipboard_append(video_url)
                messagebox.showinfo("成功", "视频链接已复制到剪贴板")
             
        except Exception as e:
            print(f"复制链接错误: {str(e)}")
            messagebox.showerror("错误", "复制链接失败")
 
    def open_in_browser(self):
        """在浏览器中打开视频"""
        try:
            selection = self.data_tree.selection()
            if not selection:
                return
             
            item = selection[0]
            values = self.data_tree.item(item)['values']
            if not values:
                return
             
            video_url = values[5]
            if video_url:
                # 确保URL格式正确
                if not video_url.startswith('http'):
                    if video_url.startswith('//'):
                        video_url = 'https:' + video_url
                    else:
                        video_url = 'https://www.douyin.com' + video_url
                     
                import webbrowser
                webbrowser.open(video_url)
             
        except Exception as e:
            print(f"打开浏览器错误: {str(e)}")
            messagebox.showerror("错误", "无法打开浏览器")
 
    def select_browser_path(self):
        """选择浏览器路径"""
        from tkinter import filedialog
         
        filename = filedialog.askopenfilename(
            title="选择Chrome浏览器程序",
            filetypes=[("Chrome程序", "chrome.exe"), ("所有文件", "*.*")],
            initialdir=os.path.dirname(self.browser_path.get())
        )
         
        if filename:
            self.browser_path.set(filename)
            # 保存设置
            try:
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump({'browser_path': filename}, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存配置失败: {str(e)}")
 
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'browser_path' in config:
                        self.browser_path.set(config['browser_path'])
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = DouyinAnalyzer(root)
        
        # 设置窗口图标
        try:
            root.iconbitmap('douyin.ico')  # 如果有图标文件可以取消注释
        except:
            pass
            
        root.mainloop()
    except Exception as e:
        logging.error(f"程序运行错误: {str(e)}", exc_info=True)
