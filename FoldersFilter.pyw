import os
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QListWidget
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QListWidget, QListWidgetItem



class FolderFilter(QWidget):
    def __init__(self):
        super().__init__()

        # 设置界面
        self.setWindowTitle('FoldersFilter')
        self.setGeometry(100, 100, 400, 400)
        # 窗口默认居中
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = int((screen.width() - size.width()) / 2)
        y = int((screen.height() - size.height()) / 2)
        self.move(x, y)

        # 创建界面组件
        self.folder_label = QLabel('待筛选的文件夹：')
        self.file_list_label = QLabel('不含有PSD文件的文件夹如下：')

        self.folder_button = QPushButton('选择文件夹', self)
        self.folder_button.clicked.connect(self.select_folder)

        self.reset_button = QPushButton('重置', self)
        self.reset_button.clicked.connect(self.reset)

        self.file_list = QListWidget()



        # 创建水平布局管理器
        hbox = QHBoxLayout()

        # 添加重置按钮和文件夹按钮到水平布局管理器中
        hbox.addWidget(self.folder_button)
        hbox.addWidget(self.reset_button)

        # 将水平布局管理器添加到窗口中
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.folder_label)
        main_layout.addLayout(hbox)
        main_layout.addWidget(self.file_list_label)
        main_layout.addWidget(self.file_list)
        self.setLayout(main_layout)
        

    def select_folder(self):
        # 弹出文件夹选择框
        dir_path = str(QFileDialog.getExistingDirectory(self, '选择文件夹'))

        # 设置已选择的文件夹路径
        self.folder_label.setText('待筛选的文件夹：{}'.format(dir_path))

        parent_dir = os.path.basename(dir_path)

        for root, dirs, files in os.walk(dir_path):
            for dir_name in dirs:
                # 子文件夹的路径
                sub_dir_path = os.path.join(root, dir_name)

                # 如果该子文件夹是目录A的一级子文件夹，则添加到控件中
                if os.path.dirname(sub_dir_path) == dir_path:
                    # 修改部分：检查子文件夹及其所有子文件夹中是否存在.psd文件
                    psd_exist = False
                    for sub_root, sub_dirs, sub_files in os.walk(sub_dir_path):
                        if any(f.endswith('.psd') for f in sub_files):
                            psd_exist = True
                            break
                    if not psd_exist:
                        item = QListWidgetItem(os.path.join(parent_dir, dir_name))
                        self.file_list.addItem(item)


    def reset(self):
        self.folder_label.setText('待筛选的文件夹：')
        self.file_list.clear()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    folder_filter = FolderFilter()
    folder_filter.show()
    sys.exit(app.exec_())