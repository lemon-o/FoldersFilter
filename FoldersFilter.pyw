import os
import sys
from tkinter.ttk import Progressbar
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget, QFileDialog, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget,QHBoxLayout
from PyQt5.QtGui import QIcon,QColor,QDesktopServices
from PyQt5.QtCore import QSettings,Qt, QUrl
import urllib.parse
from PyQt5.QtWidgets import QProgressBar
from click import progressbar


class FolderFilter(QWidget):

    #创建UI界面
    def __init__(self):
        super().__init__()

        #设置窗口图标
        self.setWindowIcon(QIcon('./icon.png'))

        # 设置界面
        self.setWindowTitle('FoldersFilter')
        self.setGeometry(100, 100, 400, 400)
        # 窗口默认居中
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = int((screen.width() - size.width()) / 2)
        y = int((screen.height() - size.height()) / 2)
        self.move(x, y)

        # 创建标签1
        self.folder_label = QLabel('待筛选的文件夹：')
        self.folder_label.setStyleSheet('margin-top: 5px; margin-bottom: 10px;')

        #创建按钮
        button_width = 180
        button_height = 30
        button_style = 'background-color: white; color: #272727; border-radius: 10px; border: 1px solid #C5C5C5;'
        
        self.folder_button = QPushButton('选择文件夹', self)
        self.folder_button.setFixedSize(button_width, button_height)
        self.folder_button.setStyleSheet(button_style)
        self.folder_button.clicked.connect(self.select_folder)

        self.reset_button = QPushButton('重置', self)
        self.reset_button.setFixedSize(button_width, button_height)
        self.reset_button.setStyleSheet(button_style)
        self.reset_button.clicked.connect(self.reset)

        #创建标签2
        label_style_1 = 'margin-top: 10px; margin-bottom: 0px;'
        label_style_2 = 'margin-top: 10px; margin-bottom: 0px; margin-left: 0px;color: #B6A338;'

        self.folder_left_label = QLabel('不含.PSD文件')
        self.folder_left_label.setStyleSheet(label_style_1)
        self.folder_left_num_label = QLabel()
        self.folder_left_num_label.setStyleSheet(label_style_2)       
        self.folder_right_label = QLabel('含有.PSD文件')
        self.folder_right_label.setStyleSheet(label_style_1)
        self.folder_right_num_label = QLabel()
        self.folder_right_num_label.setStyleSheet(label_style_2)

        #创建列表
        list_style = 'background-color: white; color: #272727; border-radius: 6px; border: 1px solid #C5C5C5;'

        self.file_left_list = QListWidget()
        self.file_left_list.setStyleSheet(list_style)
        self.file_right_list = QListWidget()
        self.file_right_list.setStyleSheet(list_style)

        #创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)   
        self.progress_bar.setMaximum(100)
        self.progress_bar.setRange(0, 100)    
        self.progress_bar.setValue(self.progress_bar.minimum())
        self.progress_bar.setStyleSheet("QProgressBar {color: transparent;border: 1px solid #F0F0F0 ;border-radius: 4px;text-align: center;} QProgressBar::chunk {background-color: #51B163;border-radius: 2px;}")
        self.progress_bar.setFixedHeight(10) # 设置进度条的高度

        #创建水平布局管理器
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()

        # 添加重置按钮和文件夹按钮到水平布局管理器中
        hbox1.addWidget(self.folder_button)
        hbox1.addWidget(self.reset_button)
        hbox2.addWidget(self.file_left_list)
        hbox2.addWidget(self.file_right_list)
        hbox3.addWidget(self.folder_left_label)
        hbox3.addWidget(self.folder_left_num_label)
        hbox3.addWidget(self.folder_right_label)
        hbox3.addWidget(self.folder_right_num_label)

        # 将组件添加到主窗口中
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.folder_label)
        main_layout.addLayout(hbox1)
        main_layout.addLayout(hbox3)
        main_layout.addLayout(hbox2)
        main_layout.addWidget(self.progress_bar)        
        self.setLayout(main_layout)

    #主程序
    def select_folder(self):    
        # 弹出文件夹选择框
        self.settings = QSettings("MyCompany", "MyApp")
        self.progress_bar.setValue(0)

        last_dir_path = self.settings.value("last_dir_path", ".")
        if not last_dir_path:  # 如果还没有保存过选择的文件夹路径，则使用当前目录作为默认路径
            last_dir_path = "."
        dir_path = str(QFileDialog.getExistingDirectory(self, '选择文件夹', last_dir_path)) 
        if not dir_path:
            QMessageBox.warning(self, '提示', '请选择要筛选的文件夹')
            return  # 如果未选择文件夹则直接返回
        else:
            self.settings.setValue("last_dir_path", dir_path)

        # 设置已选择的文件夹路径
        self.folder_label.setText('待筛选的文件夹：{}'.format(dir_path))
            
        parent_dir = os.path.basename(dir_path) 
        left_count = 0  # 不含有此类文件的子文件夹数量
        right_count = 0  # 含有此类文件的子文件夹数量
        # 统计文件夹数量
        total_count = len([name for name in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, name))])
        processed_count = 0

        for root, dirs, files in os.walk(dir_path):
            # 处理不可访问的目录
            if not os.access(root, os.R_OK):
                continue
            # 继续处理其他的目录 
            for dir_name in dirs:              
                # 子文件夹的路径
                sub_dir_path = os.path.join(root, dir_name)
                # 如果该子文件夹是目录A的一级子文件夹，则添加到控件中
                if os.path.dirname(sub_dir_path) == dir_path:
                    # 检查子文件夹及其所有子文件夹中是否存在.psd文件
                    psd_exist = False
                    for sub_root, sub_dirs, sub_files in os.walk(sub_dir_path):
                        if any(f.endswith('.psd') for f in sub_files):
                            psd_exist = True
                            break

                    if not psd_exist:
                        # 创建一个QListWidgetItem对象
                        item = QListWidgetItem()
                        # 给item设置数据，包括名称和HTML链接
                        item.setData(Qt.DisplayRole, dir_name)
                        item.setData(Qt.TextColorRole, QColor("#2F857E")) # 设置链接的颜色
                        item.setData(Qt.TextAlignmentRole, Qt.AlignLeft)   # 设置链接的对齐方式
                        item.setData(Qt.UserRole, os.path.join(parent_dir, sub_dir_path)) 
                        self.file_left_list.addItem(item)
                        left_count += 1

                    if psd_exist:
                        item = QListWidgetItem()
                        # 给item设置数据，包括名称和HTML链接
                        item.setData(Qt.DisplayRole, dir_name)
                        item.setData(Qt.TextColorRole, QColor("#39569E")) # 设置链接的颜色
                        item.setData(Qt.TextAlignmentRole, Qt.AlignLeft)   # 设置链接的对齐方式
                        item.setData(Qt.UserRole, os.path.join(parent_dir, sub_dir_path))
                        self.file_right_list.addItem(item)
                        right_count += 1
                    
                    self.folder_left_num_label.setText(f"总计：{self.file_left_list.count()}")
                    self.folder_right_num_label.setText(f"总计：{self.file_right_list.count()}")
                
                processed_count += 1
                progress_percent = int(processed_count / total_count * 100)
                self.progress_bar.setValue(progress_percent)
                           
        # 根据符合条件和不符合条件的子文件夹数量，弹出对应的提示框
        if left_count > 0 and right_count > 0:
            QMessageBox.information(self, "提示", "筛选完成，有{}个文件夹不含此类文件，有{}个文件夹含有此类文件。".format(left_count, right_count))
        elif left_count > 0:
            QMessageBox.information(self, "提示", "筛选完成，有{}个文件夹不含此类文件。".format(left_count))
        elif right_count > 0:
            QMessageBox.information(self, "提示", "筛选完成，有{}个文件夹含有此类文件。".format(right_count))
        else:
            QMessageBox.information(self, "提示", "没有符合条件的文件夹。")
                

        def item_double_clicked(list_widget):
            # 获取双击的item
            item = list_widget.currentItem()
            if item is not None:
                # 获取文件夹路径
                folder_path = item.data(Qt.UserRole)
                #url编码
                encoded_path = urllib.parse.quote(folder_path) 
                # 打开文件夹
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

        # 连接双击事件到槽函数
        self.file_left_list.itemDoubleClicked.connect(lambda: item_double_clicked(self.file_left_list))
        self.file_right_list.itemDoubleClicked.connect(lambda: item_double_clicked(self.file_right_list))       

    #重置按钮配置
    def reset(self):
        self.folder_label.setText('待筛选的文件夹：')
        self.file_left_list.clear()
        self.file_right_list.clear()
        self.folder_left_num_label.clear()
        self.folder_right_num_label.clear()
        self.progress_bar.setValue(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    folder_filter = FolderFilter()
    folder_filter.show()
    sys.exit(app.exec_())