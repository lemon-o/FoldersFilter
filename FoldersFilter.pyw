import os
import re
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QFileDialog, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget,QHBoxLayout
from PyQt5.QtGui import QIcon,QColor,QDesktopServices
from PyQt5.QtCore import QSettings,Qt, QUrl
import urllib.parse
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QComboBox, QFrame
from PIL import Image
import concurrent.futures


class FolderFilter(QWidget):

    #创建UI界面
    def __init__(self):
        super().__init__()

        #设置窗口图标
        self.setWindowIcon(QIcon('./icon.png'))
        # 设置界面
        self.setWindowTitle('FoldersFilter')
        self.setMinimumSize(650, 450) # 设置最小大小
        self.setMaximumSize(1080, 1080) # 设置最大大小
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding) # 设置大小策略
       
        # 窗口默认居中
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = int((screen.width() - size.width()) / 2)
        y = int((screen.height() - size.height()) / 2)
        self.move(x, y)

        #############创建组件   
        #创建按钮
        button_width1 = 187
        button_height1 = 30
        button_width2 = 92
        button_height2 = 30
        button_style = """
        QPushButton {
            background-color: white;
            color: #3B3E41;
            border-radius: 10px;
            border: 1px solid #C5C5C5;
        }

        QPushButton:hover {
            background-color: #CAE5DD;
            border: 1px solid #379B7E;
        }
        """

        self.folder_button = QPushButton('选择文件夹', self)
        self.folder_button.setFixedSize(button_width1, button_height1)
        self.folder_button.setStyleSheet(button_style)
        self.folder_button.clicked.connect(self.select_folder)

        self.reset_button = QPushButton('清空列表', self)
        self.reset_button.setFixedSize(button_width2, button_height2)
        self.reset_button.setStyleSheet(button_style)
        self.reset_button.clicked.connect(self.reset)

        self.refresh_button = QPushButton('刷新列表', self)
        self.refresh_button.setFixedSize(button_width2, button_height2)
        self.refresh_button.setStyleSheet(button_style)
        self.refresh_button.clicked.connect(self.refresh)

        # 创建标签1
        self.folder_label = QLabel('已选择的文件夹')
        self.folder_label.setStyleSheet('color: #3B3E41; margin-top: 5px; margin-bottom: 0px;')

        #创建下拉框
        combo_width = 85
        combo_height = 30
        combo_style_1 = 'QComboBox { color: #3B3E41; border: 1px solid #C5C5C5; border-radius: 5px; margin-top: 10px; padding-left:20px;} QComboBox::drop-down {  background-color: #C5C5C5; border: none; }'        
        combo_style_2 = 'QComboBox { color: #3B3E41; border: 1px solid #C5C5C5; border-radius: 5px; margin-top: 10px; padding-left:20px;} QComboBox::drop-down {  background-color: #C5C5C5; border: none; }'                

        self.filter_combo = QComboBox() # 文件类型选择
        self.filter_combo.setFixedSize(combo_width, combo_height)
        self.filter_combo.setStyleSheet(combo_style_1)
        self.filter_combo.setEditable(True)
        self.file_type = []
        self.filter_combo.activated.connect(self.select_folder)
        
        self.sort_combo = QComboBox()#排序选择
        self.sort_combo.setFixedSize(combo_width, combo_height)
        self.sort_combo.setStyleSheet(combo_style_2)
        sort_options = ["升序", "降序"]
        for option in sort_options:
            self.sort_combo.addItem(option)
        self.sort_combo.activated.connect(self.folders_sort)

        #创建标签2
        label_style_3 = 'color: #3B3E41; margin-top: 10px; margin-bottom: 0px; margin-left: 0px;'
        label_style_4 = 'color: #3B3E41; margin-top: 10px; margin-bottom: 0px; margin-left: 0px;'

        self.folder_type_label = QLabel('文件筛选类型：')
        self.folder_type_label.setStyleSheet(label_style_3)     
        self.folder_sort_label = QLabel('列表排序方式：')
        self.folder_sort_label.setStyleSheet(label_style_4)

        #创建标签3
        label_style_1 = 'color: #3B3E41; margin-top: 0px; margin-bottom: 0px;'
        label_style_2 = 'color: #3B3E41; margin-top: 0px; margin-bottom: 0px; margin-left: 0px;color: #B6A338;'

        self.folder_left_label = QLabel('不含')
        self.folder_left_label.setStyleSheet(label_style_1)
        self.folder_left_num_label = QLabel()
        self.folder_left_num_label.setStyleSheet(label_style_2)       
        self.folder_right_label = QLabel('含有')
        self.folder_right_label.setStyleSheet(label_style_1)
        self.folder_right_num_label = QLabel()
        self.folder_right_num_label.setStyleSheet(label_style_2)

        #创建列表
        list_style = 'background-color: white; color: #272727; border-radius: 6px; border: 1px solid #C5C5C5;'

        self.file_left_list = QListWidget()
        self.file_left_list.setStyleSheet(list_style)
        self.file_right_list = QListWidget()
        self.file_right_list.setStyleSheet(list_style)
        self.file_filter_folders_list = QListWidget()
        self.file_filter_folders_list.setStyleSheet(list_style)

        #创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)   
        self.progress_bar.setMaximum(100)
        self.progress_bar.setRange(0, 100)    
        self.progress_bar.setValue(self.progress_bar.minimum())
        self.progress_bar.setStyleSheet("QProgressBar {color: transparent;border: 1px solid #F0F0F0 ;border-radius: 4px;text-align: center;} QProgressBar::chunk {background-color: #51B163;border-radius: 2px;}")
        self.progress_bar.setFixedHeight(10) # 设置进度条的高度

        # 创建水平布局管理器
        hbox1_left_container = QWidget()
        hbox1_left = QHBoxLayout(hbox1_left_container)
        hbox1_left.addWidget(self.folder_button)
        hbox2_left_container = QWidget()
        hbox2_left = QHBoxLayout(hbox2_left_container)
        hbox2_left.addWidget(self.reset_button)
        hbox2_left.addWidget(self.refresh_button)
        hbox3_left = QHBoxLayout()
        hbox3_left.addSpacing(8) # 添加（）像素的空白占位
        hbox3_left.addWidget(self.folder_label)
        hbox4_left = QHBoxLayout() # 筛选的文件夹显示框
        hbox4_left.addSpacing(11) # 添加（）像素的空白占位
        hbox4_left.addWidget(self.file_filter_folders_list)
        hbox4_left.addSpacing(7) # 添加（）像素的空白占位
        hbox5_left = QHBoxLayout()
        hbox5_left.addSpacing(8) # 添加（）像素的空白占位
        hbox5_left.addWidget(self.folder_type_label)
        hbox5_left.addWidget(self.filter_combo)
        hbox5_left.addSpacing(10) # 添加（）像素的空白占位
        hbox6_left = QHBoxLayout()
        hbox6_left.addSpacing(8) # 添加（）像素的空白占位
        hbox6_left.addWidget(self.folder_sort_label)
        hbox6_left.addWidget(self.sort_combo)
        hbox6_left.addSpacing(10) # 添加（）像素的空白占位
        hbox1_right = QHBoxLayout()
        hbox1_right.addWidget(self.folder_left_label)
        hbox1_right.addWidget(self.folder_left_num_label)
        hbox1_right.addWidget(self.folder_right_label)
        hbox1_right.addWidget(self.folder_right_num_label)
        hbox2_right = QHBoxLayout()
        hbox2_right.addWidget(self.file_left_list)
        hbox2_right.addWidget(self.file_right_list)
        hbox3_right = QHBoxLayout()
        hbox3_right.addWidget(self.progress_bar)

        # 创建大垂直布局管理器
        vbox1 = QVBoxLayout()
        vbox1.addSpacing(25) # 添加（）像素的空白占位
        vbox1.addWidget(hbox1_left_container)
        vbox1.addWidget(hbox2_left_container)
        vbox1.addSpacing(15) # 添加（）像素的空白占位
        vbox1.addLayout(hbox3_left)
        vbox1.addLayout(hbox4_left)
        vbox1.addSpacing(15) # 添加（）像素的空白占位
        vbox1.addLayout(hbox5_left)
        vbox1.addLayout(hbox6_left)
        vbox1.addSpacing(40) # 添加（）像素的空白占位
        vbox2 = QVBoxLayout()
        vbox2.addLayout(hbox1_right)
        vbox2.addLayout(hbox2_right)
        vbox2.addLayout(hbox3_right)

        # 将组件添加到主窗口中
        main_layout = QHBoxLayout()
        vbox1_widget = QWidget()
        vbox1_widget.setLayout(vbox1)
        vbox1_widget.setFixedWidth(220) 
        main_layout.addWidget(vbox1_widget)
        main_layout.addSpacing(5) # 添加（）像素的空白占位
        main_layout.addSpacing(5) # 添加（）像素的空白占位
        main_layout.addLayout(vbox2)     
        self.setLayout(main_layout)

        # 创建垂直分隔线
        self.vline = QFrame(self)
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Plain)
        self.x = 230  # 设置垂直分隔线的位置
        self.vline.setGeometry(x, 0, 1, self.height())
        self.vline.setStyleSheet("border: 1px solid #C5C5C5;")

        ###########设置默认项
        self.settings = QSettings("lemon-o", "FoldersFilter")
        #设置默认文件类型
        last_input_left = self.settings.value("last_input_left", "", str)
        self.filter_combo.setEditText(last_input_left) 
        self.filter_combo.lineEdit().textChanged.connect(lambda text: self.settings.setValue("last_input_left", text))
        #设置默认排序方式
        last_selected_right = self.settings.value("last_selected_right", 0, int)
        self.sort_combo.setCurrentIndex(last_selected_right) 
        self.sort_combo.currentIndexChanged.connect(lambda index: self.settings.setValue("last_selected_right", index) )
        #设置默认窗口大小
        self.load_window_size()       
        #初始化变量
        self.parent_dir = None
        self.dir_path = None
        self.file_type = ""
        self.refresh_flag = True 

    # 设置垂直分隔线
    def resizeEvent(self, event):
        # 获取新的窗口宽度和高度
        new_width = event.size().width()
        new_height = event.size().height()
        # 将垂直分隔线位置和大小设置为新的窗口宽度和高度
        self.vline.setGeometry(self.x, 0, 1, new_height)

    #############主程序
    #选择文件夹
    def select_folder(self):
        self.clear_list_flag = True
        self.refresh_flag = True
        # 获取用户输入的文件类型
        file_type = self.filter_combo.currentText()        
        if not file_type:
            QMessageBox.information(self,'提示','请输入要筛选的文件类型\n例如：“.txt”')
            return
        else:
            self.settings = QSettings("lemon-o", "FoldersFilter")
            #设置进度条为初始状态
            self.progress_bar.setValue(0)
            #设置默认文件夹路径      
            last_dir_path = self.settings.value("last_dir_path", ".")
            if not last_dir_path:  # 如果还没有保存过选择的文件夹路径，则使用当前目录作为默认路径
                last_dir_path = "."
            dir_path = str(QFileDialog.getExistingDirectory(self, '选择文件夹', last_dir_path))
            if not dir_path:
                self.clear_list_flag = False
            if dir_path in [self.file_filter_folders_list.item(index).data(Qt.UserRole) for index in range(self.file_filter_folders_list.count())]:
                QMessageBox.information(self, "提示", "此文件夹已在列表中。")
                self.clear_list_flag = False
            if self.clear_list_flag == False:
                return
            if self.clear_list_flag == True:
                self.file_left_list.clear()
                self.file_right_list.clear()
                self.folder_left_num_label.clear()
                self.folder_right_num_label.clear()
                self.settings.setValue("last_dir_path", dir_path)
                # 设置已选择的文件夹路径
                item = QListWidgetItem()
                item.setData(Qt.DisplayRole, os.path.basename(dir_path))
                item.setData(Qt.TextColorRole, QColor("#761B73")) # 设置链接的颜色
                item.setData(Qt.TextAlignmentRole, Qt.AlignLeft)   # 设置链接的对齐方式
                item.setData(Qt.UserRole, dir_path)
                self.file_filter_folders_list.addItem(item)
            # 连接双击事件到槽函数
            self.file_filter_folders_list.itemDoubleClicked.connect(lambda: self.item_double_clicked(self.file_filter_folders_list))   
            self.folders_filter()

    # 文件类型筛选      
    def folders_filter(self):
        if self.file_filter_folders_list.count() == 0:
            return
        #获取选择的文件类型
        file_type = self.filter_combo.currentText()
        left_count = 0  # 不含有此类文件的子文件夹数量
        right_count = 0  # 含有此类文件的子文件夹数量
        # 统计文件夹数量
        total_count = 0
        processed_count = 0

        for i in range(self.file_filter_folders_list.count()): 
            item = self.file_filter_folders_list.item(i)
            self.parent_dir = item.data(Qt.DisplayRole)
            self.dir_path = item.data(Qt.UserRole)   
            for root, dirs, files in os.walk(self.dir_path):
                total_count += len(dirs)
                # 处理不可访问的目录
                if not os.access(root, os.R_OK):
                    continue
                # 继续处理其他的目录 
                for dir_name in dirs:              
                    # 子文件夹的路径
                    sub_dir_path = os.path.join(root, dir_name)
                    # 如果该子文件夹是目录A的一级子文件夹，则添加到控件中
                    if os.path.dirname(sub_dir_path) == self.dir_path:
                        # 检查子文件夹及其所有子文件夹中是否存在.file_type文件
                        file_type_exist = False
                        for sub_root, sub_dirs, sub_files in os.walk(sub_dir_path):
                            if any(f.endswith(file_type) for f in sub_files):
                                file_type_exist = True
                                break

                        if not file_type_exist:
                            flag_img = True
                            if os.path.isdir(os.path.join(self.parent_dir, sub_dir_path)):
                                sub_dirs = os.listdir(os.path.join(self.parent_dir, sub_dir_path))
                                for sub_dir in sub_dirs:
                                    full_sub_dir = os.path.join(self.parent_dir, sub_dir_path, sub_dir)
                                    if os.path.isdir(full_sub_dir):
                                        sub_dir_files = os.listdir(full_sub_dir)  
                                        if any(file.lower().endswith(('.jpg', '.jpeg', '.png', '.raw','.bmp', '.gif')) for file in sub_dir_files):
                                            flag_img = False  
                                            break       
                                if flag_img == True:
                                    flag_img = False #当文件夹没有任何图片文件时设置为fasle
                                    sub_dir_files = os.listdir(os.path.join(self.parent_dir, sub_dir_path))
                                    img_files = [f for f in sub_dir_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.raw','.bmp', '.gif'))]
                                    chinese_pattern = re.compile(u'[\u4e00-\u9fa5]')
                                    last_file = img_files[-1]
                                    if chinese_pattern.search(last_file):
                                        flag_img = False
                                    else:
                                        for img_file in img_files:  
                                            file_path = os.path.join(self.parent_dir, sub_dir_path, img_file)
                                            with Image.open(file_path) as img:
                                                if img.size[0] > 3000 or img.size[1] > 3000:
                                                    flag_img = True
                                                else:
                                                    flag_img = False
                                                    break
                            if flag_img == True:
                                dir_name = "未选图 " + dir_name

                            # 创建一个QListWidgetItem对象
                            item = QListWidgetItem()
                            # 给item设置数据，包括名称和HTML链接
                            item.setData(Qt.DisplayRole, dir_name)
                            item.setData(Qt.TextColorRole, QColor("#2F857E")) # 设置链接的颜色
                            item.setData(Qt.TextAlignmentRole, Qt.AlignLeft)   # 设置链接的对齐方式
                            item.setData(Qt.UserRole, os.path.join(self.parent_dir, sub_dir_path)) 
                            self.file_left_list.addItem(item)
                            left_count += 1

                        if file_type_exist:
                            item = QListWidgetItem()
                            # 给item设置数据，包括名称和HTML链接
                            item.setData(Qt.DisplayRole, dir_name)
                            item.setData(Qt.TextColorRole, QColor("#39569E")) # 设置链接的颜色
                            item.setData(Qt.TextAlignmentRole, Qt.AlignLeft)   # 设置链接的对齐方式
                            item.setData(Qt.UserRole, os.path.join(self.parent_dir, sub_dir_path))
                            self.file_right_list.addItem(item)
                            right_count += 1
                        
                        option = self.sort_combo.currentText()
                            
                        if option == "升序":
                            self.file_right_list.sortItems()
                            self.file_left_list.sortItems()
                                
                        elif option == "降序":
                            self.file_right_list.sortItems(Qt.DescendingOrder)
                            self.file_left_list.sortItems(Qt.DescendingOrder)
                                
                        self.file_right_list.update()
                        self.file_left_list.update()                     
                        
                        self.folder_left_num_label.setText(f"总计：{self.file_left_list.count()}")
                        self.folder_right_num_label.setText(f"总计：{self.file_right_list.count()}")
                    
                    processed_count += 1
                    progress_percent = int(processed_count / total_count * 100)
                    self.progress_bar.setValue(progress_percent)   

        if self.refresh_flag == False:
            QMessageBox.information(self, "提示","列表已成功刷新!")
        else:                          
            # 根据符合条件和不符合条件的子文件夹数量，弹出对应的提示框
            if left_count > 0 and right_count > 0:
                QMessageBox.information(self, "提示", "筛选完成！有{}个文件夹不含此类文件，有{}个文件夹含有此类文件。".format(left_count, right_count))
            elif left_count > 0:
                QMessageBox.information(self, "提示", "筛选完成！有{}个文件夹不含此类文件。".format(left_count))
            elif right_count > 0:
                QMessageBox.information(self, "提示", "筛选完成！有{}个文件夹含有此类文件。".format(right_count))
            else:
                QMessageBox.information(self, "提示", "没有符合筛选条件的文件夹。")
                    
            # 连接双击事件到槽函数
            self.file_left_list.itemDoubleClicked.connect(lambda: self.item_double_clicked(self.file_left_list))
            self.file_right_list.itemDoubleClicked.connect(lambda: self.item_double_clicked(self.file_right_list))
            
    def item_double_clicked(self, list_widget):
        # 获取双击的item
        item = list_widget.currentItem()
        if item is not None:
            # 获取文件夹路径
            folder_path = item.data(Qt.UserRole)
            # url编码
            encoded_path = urllib.parse.quote(folder_path)
            # 打开文件夹
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    # 进行排序      
    def folders_sort(self):  
        option = self.sort_combo.currentText()
                
        if option == "升序":
            self.file_right_list.sortItems()
            self.file_left_list.sortItems()
                
        elif option == "降序":
            self.file_right_list.sortItems(Qt.DescendingOrder) 
            self.file_left_list.sortItems(Qt.DescendingOrder)
                
        self.file_right_list.update()
        self.file_left_list.update()       
             
        
    #清空按钮配置
    def reset(self):
        if self.file_filter_folders_list.count() == 0:
            if self.file_left_list.count() == 0 or self.file_right_list.count() == 0:
                QMessageBox.information(self,'提示','请先选择文件夹')
                return
        self.parent_dir = None
        self.dir_path = None
        self.file_left_list.clear()
        self.file_right_list.clear()
        self.file_filter_folders_list.clear()
        self.folder_left_num_label.clear()
        self.folder_right_num_label.clear()
        self.progress_bar.setValue(0)

    #刷新按钮配置
    def refresh(self):
        if self.file_filter_folders_list.count() == 0:
            if self.file_left_list.count() == 0 or self.file_right_list.count() == 0:
                QMessageBox.information(self,'提示','请先选择文件夹')
                return
        self.file_left_list.clear()
        self.file_right_list.clear()
        self.folder_left_num_label.clear()
        self.folder_right_num_label.clear()
        #设置刷新标记,进入folders_filter()函数后立刻复位    
        self.refresh_flag = False 
        self.folders_filter()

    #加载窗口大小
    def load_window_size(self):
        window_size = self.settings.value('window_size', QtCore.QSize(512, 512))
        self.resize(window_size)
    #记录窗口关闭事件
    def closeEvent(self, event):
        self.settings.setValue('window_size', self.size())
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    folder_filter = FolderFilter()
    folder_filter.show()
    sys.exit(app.exec_())