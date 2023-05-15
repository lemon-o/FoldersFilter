import os
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QListWidget
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtWidgets import QHBoxLayout



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

        # 检查是否有psd文件，并输出文件名
        groups_dict = {}
        for root, dirs, files in os.walk(dir_path):
            for dir_name in dirs:
                file_list = []
                has_psd = False
                for file in os.listdir(os.path.join(root, dir_name)):
                    if file.endswith('.psd'):
                        has_psd = True
                        group_name = groups_dict.get(root)
                        if not group_name:
                            group_name = os.path.basename(root)
                            groups_dict[root] = group_name
                        break
                    else:
                        file_list.append(file)
                if not has_psd:
                    if root in groups_dict:
                        group_name = groups_dict[root]
                    else:
                        group_name = os.path.basename(root)
                        groups_dict[root] = group_name
                    group_list = []
                    for sub_folder in os.listdir(os.path.join(root, dir_name)):
                        sub_file_list = os.listdir(os.path.join(root, dir_name, sub_folder))
                        if sub_file_list:
                            continue
                        elif not os.path.basename(sub_folder).startswith('.'):
                            group_list.append(os.path.basename(sub_folder))
                    if group_list:
                        group_string = ', '.join(group_list)
                        self.file_list.addItem('{} : {}'.format(root, group_string))

                        item = self.file_list.item(self.file_list.count() - 1)
                        item.setText(group_name)

    def reset(self):
        self.folder_label.setText('待筛选的文件夹：')
        self.file_list.clear()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    folder_filter = FolderFilter()
    folder_filter.show()
    sys.exit(app.exec_())