import os

import sys
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt
from pathlib import Path

# import substance_painter.ui
import substance_painter.export
import substance_painter.project
import substance_painter.textureset
import substance_painter.logging

# Установка
# 		скопировать файлы d:\Users\YOURNAME\Documents\Adobe\Adobe Substance 3D Painter\python\plugins\
# 		скопировть пресеты в d:\Users\YOURNAME\Documents\Adobe\Adobe Substance 3D Painter\assets\export-presets\
#		включить плагин с меню сабстанс паинтера
# Настройка сабстанс файла
# 		запустить окно настройки. установить путь и настройки экспорта для каждого текстурного пресета
# 		необходимо установить путь в дифузном и аошном сабстанс файле

settings_window = None
plugin_widgets = []

# TODO
# 1. +++ экспорт аошную текстуру сразу в альфу. если нет дифузной  текстуры, то создавать её
# 2. +++ экспортировать дифуз и ао одной кнопкой. выбирать как экспортить по настройкам.
# 3. попробовать копировать минимальный imagemagic в папку плагина и оттуда запускать.
# 4. попробовать питон библиотеку image pillow или аналоги (чтобы не таскать imagemagic)
# 5. проверить на работу с разными размерами файлов


# =======================================================================================
# Utils.
# =======================================================================================
def dump(obj):
	for attr in dir(obj):
		print("obj.%s = %r" % (attr, getattr(obj, attr)))

def dump_metadata():
	metadata = substance_painter.project.Metadata("IDLE_copy_path")
	print("Path: " + str(metadata.get("copy_path")))
	print("Presets: " + str(metadata.get("presets")))

def clear_metadata():
	metadata = substance_painter.project.Metadata("IDLE_copy_path")
	metadata.set("copy_path", "")
	metadata.set("presets", "")


# =======================================================================================
# Settings window.
# =======================================================================================
class SettingsWindow(QtWidgets.QFrame):

	def __init__(self):
		super().__init__()

		self.create_window_layout()

		self.setWindowTitle("IDLE color + ao(A)")

		self.show()
		substance_painter.ui.add_dock_widget(self)
		print("Constructor")
	
	def __exit__(self, exc_type, exc_value, traceback):
		substance_painter.ui.delete_ui_element(self)
		print("Destructor")
		pass

	def create_window_layout(self):

		layout = QtWidgets.QVBoxLayout()

		layout_h = QtWidgets.QHBoxLayout()

		layout_h2 = QtWidgets.QHBoxLayout()
		label1 = QtWidgets.QLabel("Path: ")
		layout_h2.addWidget(label1)

		label1 = QtWidgets.QLabel()
		label1.setObjectName('Label_dir')

		metadata = substance_painter.project.Metadata("IDLE_copy_path")
		path = metadata.get("copy_path")
		if (path): 
			label1.setText(path)
		else:
			# label1.setStyleSheet("border :3px solid black;  background : pink")
			label1.setText("<<< SET PATH >>>")
		layout_h2.addWidget(label1)
		layout_h2.setAlignment(QtCore.Qt.AlignLeft)
		layout_h.addLayout(layout_h2)

		dir_btn = QtWidgets.QToolButton()
		dir_btn.setText("C")
		dir_btn.setFixedSize(21, 21)
		dir_btn.setToolTip("Clear copy path")
		dir_btn.clicked.connect(self.clear_copy_path_dir)
		layout_h.addWidget(dir_btn)
		layout.addLayout(layout_h)

		dir_btn = QtWidgets.QToolButton()
		dir_btn.setText("...")
		dir_btn.setFixedSize(21, 21)
		dir_btn.setToolTip("Select copy path")
		dir_btn.clicked.connect(self.set_copy_path_dir)
		layout_h.addWidget(dir_btn)
		layout.addLayout(layout_h)
		
		import ast
		presets = metadata.get("presets")
		if (presets):
			export_presets = ast.literal_eval(presets)
		else:
			export_presets = None
		
		layout_v = QtWidgets.QVBoxLayout()
		layout_v.setObjectName("ExportPresets")
		for texture_set in substance_painter.textureset.all_texture_sets():
			texture_set_name = texture_set.name()
			preset_exp, preset_ao = False, False
			if (export_presets):
				preset = export_presets[texture_set_name]
				preset_exp = preset[0]
				preset_ao = preset[1]

			layout_h = QtWidgets.QHBoxLayout()
			widget = QtWidgets.QLabel(texture_set_name)
			widget.setObjectName("Name_" + texture_set_name)
			if (export_presets):
				widget.setText(texture_set_name)
			layout_h.addWidget(widget)
			layout_h.addStretch()
			widget = QtWidgets.QLabel("Exp:")
			layout_h.addWidget(widget)
			widget = QtWidgets.QCheckBox()
			widget.setObjectName("IsExport_" + texture_set_name)
			if (export_presets and preset_exp):
				widget.setCheckState(Qt.Checked)
			else:
				widget.setCheckState(Qt.Unchecked)
			layout_h.addWidget(widget)
			widget = QtWidgets.QLabel("AO:")
			layout_h.addWidget(widget)
			widget = QtWidgets.QCheckBox()
			widget.setObjectName("IsAO_" + texture_set_name)
			if (export_presets and preset_ao):
				widget.setCheckState(Qt.Checked)
			else:
				widget.setCheckState(Qt.Unchecked)
			layout_h.addWidget(widget)
			layout_v.addLayout(layout_h)
		layout.addLayout(layout_v)
		

		layout_h = QtWidgets.QHBoxLayout()
		widget = QtWidgets.QToolButton()
		widget.setFixedSize(210, 21)
		widget.setText("Save metadata")
		widget.setToolTip("Save metadata")
		widget.clicked.connect(self.save_metadata)
		layout_h.addWidget(widget)
		layout.addLayout(layout_h)

		self.setLayout(layout)
	

	def close_window(self):
		self.hide()
		substance_painter.ui.delete_ui_element(self)
	

	def set_copy_path_dir(self):
		selected_directory = QtWidgets.QFileDialog.getExistingDirectory()
		if selected_directory:
			if os.path.isdir(str(selected_directory)):
				widget = self.findChild(QtWidgets.QLabel, "Label_dir")
				if (widget):
					widget.setText(selected_directory)


	def clear_copy_path_dir(self):
		widget = self.findChild(QtWidgets.QLabel, "Label_dir")
		if (widget):
			metadata = substance_painter.project.Metadata("IDLE_copy_path")
			metadata.set("copy_path", "")
			widget.setText("<<< SET PATH >>>")

	
	def save_metadata(self):
		metadata = substance_painter.project.Metadata("IDLE_copy_path")

		widget = self.findChild(QtWidgets.QLabel, 'Label_dir')
		if (widget):
			path = widget.text()
			if (not os.path.isdir(path)):
				path = ""
			metadata.set("copy_path", path)

		widget = self.findChild(QtWidgets.QVBoxLayout, "ExportPresets")
		if (widget):
			# preset
			# {'Texture_name': [True, False], ...}

			presets = {}

			boxes = widget.findChildren(QtWidgets.QHBoxLayout)
			for box in boxes:
				preset_name = box.itemAt(0).widget().objectName()[5:]
				preset_exp = box.itemAt(3).widget().isChecked()
				preset_ao = box.itemAt(5).widget().isChecked()
				
				presets[preset_name] = [preset_exp, preset_ao]

			metadata.set("presets", str(presets))


# =======================================================================================
# Show texture setting window.
# =======================================================================================
def show_texture_setting_window():
	if not substance_painter.project.is_open():
		substance_painter.logging.error("Project not open.")
		return
	
	global settings_window
	settings_window = SettingsWindow()


# =======================================================================================
# Copy texture.
# =======================================================================================
def copy_texture(project_file_path, dest_path, file_name):
	import os
	import shutil
	
	if not os.path.exists(dest_path):
		os.makedirs(dest_path)
	
	file_name += "_DF.tga"
	src_file = os.path.join(project_file_path, file_name)
	dst_file = os.path.join(dest_path, file_name)
	if os.path.exists(dst_file):
		# in case of the src and dst are the same file
		if os.path.samefile(src_file, dst_file):
			return
		os.remove(dst_file)
	# shutil.move(src_file, dest_path)
	shutil.copy(src_file, dest_path)

	print("Copy texture {0} to {1}".format(file_name, dest_path))


# =======================================================================================
# Add alpha.
# =======================================================================================
def add_alpha(project_file_path, material_name):
	from os.path import isfile, join, dirname, basename

	project_path = dirname(project_file_path)

	exported_file = material_name + "_DF.tga"
	ao_file = material_name + "_AO.tga"
	magick_file_path = "magick.exe"
	exported_file_path = join(project_path, exported_file)
	ao_file_path = join(project_path, ao_file)
	if not isfile(exported_file_path) and isfile(ao_file_path):
		# create empty diffuse texture.
		import subprocess
		# magick.exe -size 2048x2048 xc:"#ffffff" D:/test.tga
		# magick.exe D:/test.tga -transparent black D:/test.tga
		cmd = "{0} {1} {2}".format('"' + magick_file_path + '"', " -size 2048x2048 xc:" + '"' + "#ffffff"  + '"', ' "' + exported_file_path + '"')
		print("Create empty image.\n" + cmd)
		subprocess.call(cmd, shell=True)
	if isfile(exported_file_path) and isfile(ao_file_path):
		# Add alpha from ao texture.
		import subprocess
		cmd = "{0} {1} {2} {3} {4}".format('"' + magick_file_path + '"', '"' + exported_file_path + '"', '"' + ao_file_path + '"', "-compose CopyOpacity -composite", '"' + exported_file_path + '"')
		subprocess.call(cmd, shell=True)

	if isfile(exported_file_path) and not isfile(ao_file_path):
		# Add white alpha.
		import subprocess
		cmd = "{0} {1} {2} {3}".format('"' + magick_file_path + '"', '"' + exported_file_path + '"', "-alpha on", '"' + exported_file_path + '"')
		subprocess.call(cmd, shell=True)


def pyvips_exapmle():
	import sys 
	import pyvips

	if len(sys.argv) < 3:
		print("usage: join outfile in1 in2 in3 ...")
		sys.exit(1)

	def imopen(filename):
		im = pyvips.Image.new_from_file(filename, access="sequential")
		if not im.hasalpha():
			im = im.addalpha()

		return im

	images = [imopen(filename) for filename in sys.argv[2:]]
	image = images[0]
	for tile in images[1:]:
		image = image.join(tile, "horizontal", expand=True)

	image.write_to_file(sys.argv[1])

# =======================================================================================
# Export textures.
# =======================================================================================
def export_ao_texture(project_path, name):
	export_preset = substance_painter.resource.ResourceID(context="your_assets", name="IDLE_Buildings_A(AO)")
	if export_preset == None:
		substance_painter.logging.error("IDLE_Buildings_A(AO) export preset not found.")
		return

	# Build the configuration
	config = {
		"exportShaderParams" 	: False,
		"exportPath" 			: project_path,
		"exportList"			: [],
		"exportPresets" 		: [ { "name" : "default", "maps" : [] } ],
		"defaultExportPreset" 	: export_preset.url(),
		"exportParameters" 		: [
			{
				"parameters"	: { "dithering": True, "paddingAlgorithm": "infinite" }
			}
		]
	}

	config["exportList"] = [{"rootPath" : name}]

	# Export texture.
	export_result = substance_painter.export.export_project_textures( config )

	if export_result.status != substance_painter.export.ExportStatus.Success:
		substance_painter.logging.error("Export error: {0}".format(export_result.message))


def export_diffuse_texture(project_path, name):
	export_preset = substance_painter.resource.ResourceID(context="your_assets", name="IDLE_Buildings")
	if export_preset == None:
		substance_painter.logging.error("IDLE_Buildings export preset not found.")
		return

	# Build the configuration
	config = {
		"exportShaderParams" 	: False,
		"exportPath" 			: project_path,
		"exportList"			: [],
		"exportPresets" 		: [ { "name" : "default", "maps" : [] } ],
		"defaultExportPreset" 	: export_preset.url(),
		"exportParameters" 		: [
			{
				"parameters"	: { "dithering": True, "paddingAlgorithm": "infinite" }
			}
		]
	}

	config["exportList"] = [{"rootPath" : name}]

	# Export texture.
	export_result = substance_painter.export.export_project_textures( config )

	if export_result.status != substance_painter.export.ExportStatus.Success:
		substance_painter.logging.error("Export error: {0}".format(export_result.message))


def export_textures():
	if not substance_painter.project.is_open() :
		substance_painter.logging.error("Project file not open.")
		return
	
	project_path = substance_painter.project.file_path()
	project_path = os.path.dirname(project_path) + "/"

	import ast
	metadata = substance_painter.project.Metadata("IDLE_copy_path")
	export_presets = ast.literal_eval(metadata.get("presets"))

	for name, value in export_presets.items():
		if (value[0] and value[1]):
			# export ao
			export_ao_texture(project_path, name)
			
		if (value[0] and not value[1]):
			# export diffuse
			export_diffuse_texture(project_path, name)
	
	for name, value in export_presets.items():
		# add ao to alpha
		add_alpha(project_path, name)
		
		copy_path = metadata.get("copy_path")
		if (copy_path and value[0]):
			copy_texture(project_path, copy_path, name)

	
# =======================================================================================
# Plugin.
# =======================================================================================
def start_plugin():

	# Menu.
	Action = QtGui.QAction("Export textures with AO", triggered=export_textures)
	plugin_widgets.append(Action)

	Action3 = QtGui.QAction("Show settings window", triggered=show_texture_setting_window)
	plugin_widgets.append(Action3)

	Action4 = QtGui.QAction("Dump metadata", triggered=dump_metadata)
	plugin_widgets.append(Action4)

	Action5 = QtGui.QAction("Clear metadata", triggered=clear_metadata)
	plugin_widgets.append(Action5)


	menu = QtWidgets.QMenu("IDLE Export")
	menu.addAction(Action)
	menu.addAction(Action3)
	menu.addAction(Action4)
	menu.addAction(Action5)
	substance_painter.ui.add_menu(menu)
	plugin_widgets.append(menu)

	# Export button.
	path_this_file = os.path.abspath(__file__)
	path_this_dir = os.path.dirname(path_this_file)
	path_icons = os.path.join(path_this_dir, 'icons')
	path_icon = os.path.join(path_icons, "Idle_export.png")

	widget = QtWidgets.QToolButton()
	widget.clicked.connect(export_textures)
	widget.setFixedSize(21, 21)
	widget.setToolTip("IDLE Export")
	widget.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
	widget.setIcon(QtGui.QIcon(path_icon))

	substance_painter.ui.add_plugins_toolbar_widget(widget)
	plugin_widgets.append(widget)


def close_plugin():
	# delete settings window
	global settings_window
	if (settings_window):
		del settings_window

	# delete widgets
	for widget in plugin_widgets:
		substance_painter.ui.delete_ui_element(widget)

	plugin_widgets.clear()


if __name__ == "__main__":
	start_plugin()