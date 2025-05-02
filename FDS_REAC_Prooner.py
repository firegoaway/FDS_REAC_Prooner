import sys
import traceback
import re
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
                            QTextEdit, QMessageBox, QGroupBox, QStatusBar, QFileDialog, QFormLayout,
                            QSpacerItem, QSizePolicy, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPalette, QColor, QDoubleValidator, QFont, QIcon

class FDSReacCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        icon_path = os.path.join(parent_directory, '.gitpics', 'favicon.ico')
        self.setWindowIcon(QIcon(icon_path))
        # Устанавливаем заголовок окна  
        self.setWindowTitle("FRP v1.0")
        self.setMinimumSize(1280, 720)  # Устанавливаем минимальный размер окна
        
        # Держим путь к импортированному файлу
        self.imported_file_path = None
        
        # Храним ID топлива (по умолчанию "Fuel")
        self.fuel_id = "Fuel"
        
        # Константы для молярных масс
        self.W_O2 = 32.0
        self.W_CO2 = 44.0
        self.W_CO = 28.0
        self.W_H2O = 18.0
        self.W_SOOT = 12.0
        self.W_HCl = 36.5
        self.W_N2 = 28.0
        
        self._setup_palette()
        self._setup_ui()
        self.statusBar.showMessage("Готово") # Показываем начальное сообщение после настройки UI
    
    def _setup_palette(self):
        """Устанавливает цветовую палитру приложения."""
        palette = QPalette()
        # Определяем современную, светлую цветовую схему
        palette.setColor(QPalette.ColorRole.Window, QColor(248, 250, 252))  # Очень светло-синий
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 41, 59))  # Темно-синий
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))  # Чистый белый
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(241, 245, 249))  # Светло-синий
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))  # Белый tooltip
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(30, 41, 59))  # Темно-синий
        palette.setColor(QPalette.ColorRole.Text, QColor(30, 41, 59))  # Темно-синий
        palette.setColor(QPalette.ColorRole.Button, QColor(186, 230, 253))  # Светло-синие кнопки
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(3, 105, 161))  # Темно-синий текст на кнопках
        palette.setColor(QPalette.ColorRole.Highlight, QColor(125, 211, 252))  # Светло-синий выделенный текст
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(30, 41, 59))  # Темно-синий текст для контраста
        self.setPalette(palette)
    
    def _setup_ui(self):
        """Устанавливает основные элементы и макет UI."""
        # Устанавливаем шрифт приложения
        app_font = QFont("Segoe UI", 10)  # Современный шрифт с хорошей читаемостью
        QApplication.setFont(app_font)
        
        # Создаем строку состояния с современным стилем
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("QStatusBar { background-color: rgb(241, 245, 249); color: rgb(30, 41, 59); }")
        self.setStatusBar(self.statusBar)
        
        # Создаем область прокрутки для обработки изменения размера
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.setCentralWidget(scroll_area)
        
        # Создаем центральный виджет с отступами
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        
        # Основной макет с лучшим отступом
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Добавляем отступы вокруг всех сторон
        main_layout.setSpacing(15)
        
        # Заголовок/заголовок приложения
        header = QLabel("Калькулятор параметров сложной стехиометрии в реакторе FDS 6.8.0")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: rgb(3, 105, 161); padding: 10px;")
        main_layout.addWidget(header)
        
        # Горизонтальный макет для ввода и помощи
        input_help_layout = QHBoxLayout()
        input_help_layout.setSpacing(20)
        
        # Форма ввода
        input_group = self._create_input_group()
        input_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        input_help_layout.addWidget(input_group, 6)  # 60% of width
        
        # Текст помощи
        help_group = QGroupBox("Руководство по расчетам")
        help_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        help_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bfdbfe;
                border-radius: 8px;
                margin-top: 1ex;
                background-color: rgba(241, 245, 249, 120);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        help_layout = QVBoxLayout(help_group)
        help_layout.setContentsMargins(15, 15, 15, 15)
        help_label = self._create_help_label()
        help_layout.addWidget(help_label)
        input_help_layout.addWidget(help_group, 4)  # 40% of width
        
        main_layout.addLayout(input_help_layout)
        
        # Горизонтальный разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #bfdbfe;")
        main_layout.addWidget(separator)
        
        # Кнопки
        buttons_layout = self._create_buttons_layout()
        main_layout.addLayout(buttons_layout)
        
        # Область результатов
        results_group = self._create_results_area()
        main_layout.addWidget(results_group)
    
    def _create_input_group(self):
        """Создает группу полей ввода."""
        input_group = QGroupBox("Параметры топлива")
        input_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bfdbfe;
                border-radius: 8px;
                margin-top: 1ex;
                background-color: rgba(255, 255, 255, 200);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                background-color: white;
                min-width: 120px;
            }
            QLineEdit:focus {
                border: 2px solid #7dd3fc;
            }
            QLabel {
                font-weight: normal;
                min-width: 160px;
            }
        """)
        
        input_layout = QFormLayout()
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setHorizontalSpacing(15)
        input_layout.setVerticalSpacing(12)
        input_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        input_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Создаем поля ввода
        self.inputs = {}
        
        # Определяем значения по умолчанию для тестирования
        default_values = {
            "heat_release": "31700",
            "soot_yield": "0.1",
            "o2_consumption": "1.5",
            "co2_yield": "2.5",
            "co_yield": "0.05",
            "hcl_yield": "0.01",
            "molar_mass": "104.3233"
        }
        
        parameters = [
            ("Низшая теплота сгорания (кДж/кг):", "heat_release", "Введите теплоту сгорания (неотрицательное значение)"),
            ("Дымообразующая способность (Нп*м²/кг):", "soot_yield", "Введите значение дымообразующей способности (неотрицательное значение)"),
            ("Потребление кислорода (кг/кг):", "o2_consumption", "Введите значение потребления кислорода (неотрицательное значение)"),
            ("Выход CO₂ (кг/кг):", "co2_yield", "Введите значение выделения CO₂ (неотрицательное значение)"),
            ("Выход CO (кг/кг):", "co_yield", "Введите значение выделения CO (неотрицательное значение)"),
            ("Выход HCl (кг/кг):", "hcl_yield", "Введите значение выделения HCl (неотрицательное значение) или оставьте пустым для нуля"),
            ("Молярная масса (г/моль):", "molar_mass", "Введите значение молярной массы (должно быть положительным значением)")
        ]
        
        for label_text, input_name, tooltip in parameters:
            label = QLabel(label_text)
            self.inputs[input_name] = QLineEdit()
            self.inputs[input_name].setMinimumWidth(150)
            self.inputs[input_name].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.inputs[input_name].setPlaceholderText(tooltip.split('(')[0].strip())
            self.inputs[input_name].setToolTip(tooltip)
            
            # Добавляем QDoubleValidator для числовых вводов
            if input_name == "molar_mass":
                # Молярная масса должна быть положительной
                validator = QDoubleValidator(0.0001, 999999.9999, 4, self)
                validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            elif input_name != "hcl_yield": # Все остальные должны быть неотрицательными
                validator = QDoubleValidator(0.0, 999999.9999, 4, self)
                validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            else: # HCl может быть пустым или неотрицательным
                # Мы будем обрабатывать проверку HCl отдельно в validate_inputs
                pass
            
            # Применяем валидатор, если он создан
            if input_name != "hcl_yield":
                 self.inputs[input_name].setValidator(validator)

            # Устанавливаем значения по умолчанию
            if input_name in default_values:
                self.inputs[input_name].setText(default_values[input_name])
            input_layout.addRow(label, self.inputs[input_name])
            
        # Добавляем заметку о ID топлива
        fuel_id_layout = QHBoxLayout()
        fuel_id_label = QLabel("Текущий ID топлива:")
        fuel_id_label.setStyleSheet("font-style: italic;")
        self.fuel_id_value = QLabel(self.fuel_id)
        self.fuel_id_value.setStyleSheet("font-weight: bold; color: #0369a1;")
        fuel_id_layout.addWidget(fuel_id_label)
        fuel_id_layout.addWidget(self.fuel_id_value)
        fuel_id_layout.addStretch()
        
        input_layout.addRow("", QWidget())  # Добавляем некоторое пространство
        input_layout.addRow("", fuel_id_layout)
        
        input_group.setLayout(input_layout)
        return input_group
    
    def _create_help_label(self):
        """Creates the help text label."""
        help_text = """
        <div style="line-height: 1.4;">
        <p><b style="color: #0369a1;">Формулы расчета:</b></p>
        <ol style="padding-left: 20px;">
        <li>Air = O<sub>2</sub> + 3.7619 N<sub>2</sub></li>
        <li>Fuel + ϑ<sub>O₂</sub> Air → Products</li>
        <li>ϑ<sub>O₂</sub> = (W<sub>Fuel</sub> / W<sub>O₂</sub>) × Y<sub>O₂</sub></li>
        <li>ϑ<sub>CO₂</sub> = (W<sub>Fuel</sub> / W<sub>CO₂</sub>) × Y<sub>CO₂</sub></li>
        <li>ϑ<sub>CO</sub> = (W<sub>Fuel</sub> / W<sub>CO</sub>) × Y<sub>CO</sub></li>
        <li>ϑ<sub>Soot</sub> = (W<sub>Fuel</sub> / W<sub>Soot</sub>) × (Y<sub>Soot</sub> / 9500)</li>
        <li>ϑ<sub>HCl</sub> = (W<sub>Fuel</sub> / W<sub>HCl</sub>) × Y<sub>HCl</sub></li>
        <li>Y<sub>H₂O</sub> = 1 + Y<sub>O₂</sub> - Y<sub>CO₂</sub> - Y<sub>CO</sub> - (Y<sub>Soot</sub> / 9500) - Y<sub>HCl</sub></li>
        <li>ϑ<sub>H₂O</sub> = (W<sub>Fuel</sub> / W<sub>H₂O</sub>) × Y<sub>H₂O</sub></li>
        <li>ϑ<sub>N₂</sub> = 3.7619 × ϑ<sub>O₂</sub></li>
        </ol>
        <p style="color: #475569; font-style: italic; margin-top: 10px;">Обратите внимание: Y обозначает выделение (кг/кг или Нп*м²/кг для дымообразующей способности), ϑ обозначает стехиометрический коэффициент (моли).</p>
        </div>
        """
        help_label = QLabel(help_text)
        help_label.setTextFormat(Qt.TextFormat.RichText)
        help_label.setWordWrap(True)
        help_label.setContentsMargins(10, 10, 10, 10)
        help_label.setStyleSheet("""
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            color: #334155;
        """)
        return help_label
    
    def _create_buttons_layout(self):
        """Создает макет для кнопок действий."""
        # Стиль кнопки
        button_style = """
            QPushButton {
                background-color: #bae6fd;
                color: #0369a1;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #7dd3fc;
            }
            QPushButton:pressed {
                background-color: #0284c7;
                color: white;
            }
            QPushButton:disabled {
                background-color: #e2e8f0;
                color: #94a3b8;
            }
        """
        
        # Главный контейнер
        buttons_container_layout = QVBoxLayout()
        buttons_container_layout.setSpacing(15)
        
        # Первая строка
        calc_clear_layout = QHBoxLayout()
        calc_clear_layout.setSpacing(10)
        
        self.calculate_button = QPushButton("Рассчитать")
        self.calculate_button.setIcon(QIcon.fromTheme("calculator"))
        self.calculate_button.setStyleSheet(button_style)
        self.calculate_button.setToolTip("Рассчитать параметры REAC на основе ввода")
        self.calculate_button.clicked.connect(self.calculate_parameters)
        self.calculate_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        self.copy_button = QPushButton("Скопировать результаты")
        self.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_button.setStyleSheet(button_style)
        self.copy_button.setToolTip("Скопировать сгенерированные REAC строки в буфер обмена")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setEnabled(False)
        self.copy_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        self.clear_button = QPushButton("Очистить вводы")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.setStyleSheet(button_style)
        self.clear_button.setToolTip("Очистить все поля ввода и результаты")
        self.clear_button.clicked.connect(self.clear_inputs)
        self.clear_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        calc_clear_layout.addWidget(self.calculate_button)
        calc_clear_layout.addWidget(self.copy_button)
        calc_clear_layout.addWidget(self.clear_button)
        calc_clear_layout.addStretch()
        
        # Second row
        file_ops_layout = QHBoxLayout()
        file_ops_layout.setSpacing(10)
        
        self.import_button = QPushButton("Импортировать из FDS")
        self.import_button.setIcon(QIcon.fromTheme("document-open"))
        self.import_button.setStyleSheet(button_style)
        self.import_button.setToolTip("Импортировать параметры из существующего файла FDS")
        self.import_button.clicked.connect(self.import_fds_file)
        self.import_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        self.save_fds_button = QPushButton("Сохранить в FDS")
        self.save_fds_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_fds_button.setStyleSheet(button_style)
        self.save_fds_button.setToolTip("Сохранить сгенерированные REAC строки в файл FDS")
        self.save_fds_button.clicked.connect(self.save_to_fds_file)
        self.save_fds_button.setEnabled(False)
        self.save_fds_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        file_ops_layout.addStretch()
        file_ops_layout.addWidget(self.import_button)
        file_ops_layout.addWidget(self.save_fds_button)
        
        buttons_container_layout.addLayout(calc_clear_layout)
        buttons_container_layout.addLayout(file_ops_layout)
        
        return buttons_container_layout
    
    def _create_results_area(self):
        """Создает область отображения результатов."""
        results_group = QGroupBox("Сгенерированная реакция")
        results_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        results_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bfdbfe;
                border-radius: 8px;
                margin-top: 1ex;
                background-color: rgba(255, 255, 255, 200);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 5px;
                padding: 10px;
                color: #334155;
            }
        """)
        
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(15, 15, 15, 15)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)
        self.results_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.results_text.setFont(QFont("Consolas", 10))
        
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        return results_group
    
    def validate_inputs(self, silent=False):
        """Проверяет все входные данные пользователя, чтобы убедиться, что они являются неотрицательными числами"""
        valid_inputs = {}
        
        for name, input_field in self.inputs.items():
            # Сбросить цвет фона
            input_field.setStyleSheet("")
            
            input_text = input_field.text().strip().replace(',', '.') # Заменить запятую на точку для локалей
            
            # Выделение HCl который не имеет валидатора
            if name == "hcl_yield" and not input_text:
                valid_inputs[name] = 0.0
                continue
                
            try:
                # Для полей с валидаторами мы можем доверять вводу, но все равно нужно преобразовать в float и проверить диапазон, если необходимо
                # Особенно для HCl, который не имеет валидатора
                float_value = float(input_text)
                if float_value < 0:
                    if not silent:
                        self.statusBar.showMessage(f"Ошибка: Значение для {name} должно быть неотрицательным")
                        # Подсветка ошибочного поля
                        input_field.setStyleSheet("background-color: rgba(254, 202, 202, 150);")
                    return None
                # Дополнительная проверка для молярной массы (должна быть > 0)
                if name == "molar_mass" and float_value <= 0:
                    if not silent:
                        self.statusBar.showMessage(f"Ошибка: Значение для молярной массы должно быть положительным")
                        # Подсветка ошибочного поля
                        input_field.setStyleSheet("background-color: rgba(254, 202, 202, 150);")
                        QMessageBox.warning(self, "Неверный ввод", 
                                          f"Значение для молярной массы должно быть положительным.")
                    return None
                    
                valid_inputs[name] = float_value
            except ValueError:
                if not silent:
                    self.statusBar.showMessage(f"Ошибка: Значение для {name} должно быть допустимым числом")
                    # Подсветка ошибочного поля
                    input_field.setStyleSheet("background-color: rgba(254, 202, 202, 150);")
                    QMessageBox.warning(self, "Неверный ввод", 
                                      f"Значение для {name} должно быть допустимым числом.")
                return None
                
        return valid_inputs
    
    def calculate_parameters(self, silent=False):
        """Рассчитывает параметры REAC FDS на основе ввода пользователя"""
        try:
            if not silent:
                self.statusBar.showMessage("Рассчитываются параметры...")
            
            valid_inputs = self.validate_inputs(silent)
            if not valid_inputs:
                return
            
            # Сбросить все стили полей ввода в нормальное состояние
            for input_field in self.inputs.values():
                input_field.setStyleSheet("")
                
            # Извлечь проверенные входные данные
            heat_release = valid_inputs["heat_release"]
            soot_yield = valid_inputs["soot_yield"] / 9500.0  # Convert as per requirement
            o2_consumption = valid_inputs["o2_consumption"]
            co2_yield = valid_inputs["co2_yield"]
            co_yield = valid_inputs["co_yield"]
            hcl_yield = valid_inputs["hcl_yield"]
            molar_mass = valid_inputs["molar_mass"]
            
            # Рассчитать объемные доли, используя формулы
            V_O2 = (molar_mass / self.W_O2) * o2_consumption
            V_CO2 = (molar_mass / self.W_CO2) * co2_yield
            V_CO = (molar_mass / self.W_CO) * co_yield
            V_SOOT = (molar_mass / self.W_SOOT) * soot_yield
            V_HCl = (molar_mass / self.W_HCl) * hcl_yield
            
            # Рассчитать V_H2O используя формулу (26) из изображения
            # Примечание: Нам нужно использовать выходы, а не объемные доли
            Y_H2O = 1 + o2_consumption - co2_yield - co_yield - soot_yield - hcl_yield
            V_H2O = (molar_mass / self.W_H2O) * Y_H2O
            
            # Рассчитать V_N2 используя формулу (24) из изображения
            V_N2 = 3.7619 * V_O2
            
            # Рассчитать массу реагентов: -(Fuel + O2 + N2)
            # Это представляет собой общую массу топлива (-1) и воздуха (-V_O2 * [1 + 3.7619*(W_N2/W_O2)])
            mass_reactants = -(1 + V_O2 * (1 + 3.7619 * (self.W_N2 / self.W_O2)))

            # Определить компоненты и объемные доли для PRODUCTS на основе того, является ли HCl > 0
            product_spec_ids = ['SOOT', 'CARBON DIOXIDE', 'CARBON MONOXIDE']
            product_volume_fractions = [V_SOOT, V_CO2, V_CO]

            if hcl_yield > 1e-9: # Использовать небольшой допуск для сравнения с плавающей запятой
                product_spec_ids.append('HYDROGEN CHLORIDE')
                product_volume_fractions.append(V_HCl)
                final_product_index = 6
            else:
                final_product_index = 5 # Опустить HCl

            product_spec_ids.extend(['WATER VAPOR', 'NITROGEN'])
            product_volume_fractions.extend([V_H2O, V_N2])

            # Отформатировать строки для SPEC
            product_spec_id_str = ",".join([f"'{s}'" for s in product_spec_ids])
            product_vf_str = ",".join([f"{v:.15f}" for v in product_volume_fractions])

            # Сгенерировать REAC строки
            reac_lines = f"""&SPEC ID='OXYGEN' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='NITROGEN' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='CARBON DIOXIDE' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='CARBON MONOXIDE' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='HYDROGEN CHLORIDE' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='WATER VAPOR' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='SOOT' LUMPED_COMPONENT_ONLY=.True./
&SPEC ID='{self.fuel_id}' MW={molar_mass}/ 
&SPEC ID='AIR' BACKGROUND=.True. SPEC_ID(1:2)='OXYGEN','NITROGEN' VOLUME_FRACTION(1:2)=1,3.7619/
&SPEC ID='PRODUCTS' SPEC_ID(1:{final_product_index})={product_spec_id_str} VOLUME_FRACTION(1:{final_product_index})={product_vf_str}/
&REAC FUEL='{self.fuel_id}' HEAT_OF_COMBUSTION={heat_release} SPEC_ID_NU(1:3)='{self.fuel_id}','AIR','PRODUCTS' NU(1:3)=-1,{mass_reactants:.4f},1 REAC_ATOM_ERROR=1E5 REAC_MASS_ERROR=1E4 CHECK_ATOM_BALANCE=.False./
"""

            self.results_text.setText(reac_lines)
            self.copy_button.setEnabled(True)
            self.save_fds_button.setEnabled(self.imported_file_path is not None)
            
            if not silent:
                # Показать сообщение об успешном завершении с эффектом затухания
                self.statusBar.showMessage("Расчет завершен. REAC строки сгенерированы.")
                
                # Подсветка области результатов на короткое время для привлечения внимания
                orig_style = self.results_text.styleSheet()
                self.results_text.setStyleSheet("background-color: rgba(187, 247, 208, 150); border: 1px solid #4ade80;")
                
                # Reset after a delay (this is simplified - in a real app you might use QTimer)
                QApplication.processEvents()
                import time
                time.sleep(0.5)
                self.results_text.setStyleSheet(orig_style)
            else:
                self.statusBar.showMessage("Расчет завершен. REAC строки сгенерированы.")
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка: {str(e)}")
            QMessageBox.critical(self, "Ошибка расчета", 
                              f"Произошла ошибка при расчете:\n{str(e)}\n\n{traceback.format_exc()}")
    
    def copy_to_clipboard(self):
        """Копирует сгенерированные REAC строки в буфер обмена"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.results_text.toPlainText())
            
            # Показать индикаторы успеха
            self.statusBar.showMessage("REAC строки скопированы в буфер обмена!")
            
            # Визуальная обратная связь - подсветка кнопки копирования на короткое время
            orig_style = self.copy_button.styleSheet()
            self.copy_button.setStyleSheet("""
                background-color: #4ade80;
                color: #064e3b;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-width: 120px;
            """)
            
            # Сбросить после задержки
            QApplication.processEvents()
            import time
            time.sleep(0.3)
            self.copy_button.setStyleSheet(orig_style)
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка копирования в буфер обмена: {str(e)}")
            QMessageBox.warning(self, "Ошибка копирования", f"Ошибка копирования в буфер обмена: {str(e)}")
    
    def clear_inputs(self):
        """Очищает все поля ввода и результаты"""
        for input_field in self.inputs.values():
            input_field.clear()
        self.results_text.clear()
        self.copy_button.setEnabled(False)
        self.save_fds_button.setEnabled(False)
        self.imported_file_path = None
        self.fuel_id = "Fuel"  # Сбросить ID топлива на значение по умолчанию
        self.fuel_id_value.setText(self.fuel_id)  # Обновить отображение ID топлива
        self.statusBar.showMessage("Входные данные и результаты очищены.")
        
    def import_fds_file(self):
        """Импортирует параметры из файла FDS"""
        try:
            # Открыть диалоговое окно для выбора файла FDS
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Открыть файл FDS", "", "FDS файлы (*.fds);;Все файлы (*)"
            )
            
            if not file_path:
                return  # Пользователь отменил
                
            self.statusBar.showMessage(f"Загрузка файла FDS: {file_path}")
            self.imported_file_path = file_path  # Сохранить путь к импортированному файлу
            
            # Читать файл FDS
            with open(file_path, 'r') as file:
                fds_content = file.read()
            
            # Инициализировать словарь параметров
            params = {}
            
            # Сначала извлечь ID топлива из REAC строки
            fuel_id_match = re.search(r'&REAC\s+FUEL=[\'"]([^\'"]+)[\'"]', fds_content, re.DOTALL | re.IGNORECASE)
            fuel_id = "Fuel"  # Значение по умолчанию
            if fuel_id_match:
                fuel_id = fuel_id_match.group(1)
            
            # Сохранить ID топлива в классе
            self.fuel_id = fuel_id
            # Обновить отображение ID топлива
            self.fuel_id_value.setText(self.fuel_id)
            
            # Извлечь HEAT_OF_COMBUSTION из REAC
            heat_match = re.search(r'&REAC.*?HEAT_OF_COMBUSTION\s*=\s*(\d+\.?\d*)', fds_content, re.DOTALL | re.IGNORECASE)
            if heat_match:
                params['heat_release'] = heat_match.group(1)
            
            # Escape the fuel_id for use in regex
            escaped_fuel_id = re.escape(fuel_id)
            # Извлечь MW из Fuel SPEC используя извлеченный ID топлива
            mw_match = re.search(rf"&SPEC\s+ID=['\"]({escaped_fuel_id})['\"].*?MW\s*=\s*(\d+\.?\d*)", fds_content, re.DOTALL | re.IGNORECASE)
            if mw_match:
                params['molar_mass'] = mw_match.group(2)
                molar_mass = float(params['molar_mass'])
                self.statusBar.showMessage(f"Found molar mass {molar_mass} for fuel ID '{fuel_id}'")
            else:
                # Не можем продолжить без молярной массы
                self.statusBar.showMessage(f"Ошибка: Не удалось найти молярную массу для ID топлива '{fuel_id}' в файле FDS.")
                QMessageBox.warning(self, "Предупреждение при импорте", f"Не удалось найти молярную массу для ID топлива '{fuel_id}' в файле FDS.")
                return
            
            # Извлечь VOLUME_FRACTION значения из PRODUCTS SPEC
            # Regex to match 5 or 6 species, making HCl optional
            products_pattern = r"&SPEC ID=['\"]PRODUCTS['\"]\s*.*?SPEC_ID\s*\(\s*1\s*:\s*(?P<count>[56])\s*\)\s*=\s*(?P<ids>.*?)\s*VOLUME_FRACTION\s*\(\s*1\s*:\s*(?P=count)\s*\)\s*=\s*(?P<vfs>[\d\.\s,E\-]+)/"
            products_match = re.search(products_pattern, fds_content, re.DOTALL | re.IGNORECASE)

            # Initialize V_ variables to None
            V_SOOT, V_CO2, V_CO, V_HCl, V_H2O, V_N2 = None, None, None, None, None, None

            if products_match:
                count = int(products_match.group('count'))
                ids_str = products_match.group('ids').strip()
                vfs_str = products_match.group('vfs').strip()
                
                # Extract IDs and VFs
                ids = [i.strip("' ") for i in ids_str.split(',')]
                vfs = [float(v.strip()) for v in vfs_str.split(',')]
                
                if len(ids) == count and len(vfs) == count:
                    products_dict = dict(zip(ids, vfs))
                    
                    # Assign V_ variables based on found IDs
                    V_SOOT = products_dict.get('SOOT')
                    V_CO2 = products_dict.get('CARBON DIOXIDE')
                    V_CO = products_dict.get('CARBON MONOXIDE')
                    V_HCl = products_dict.get('HYDROGEN CHLORIDE') # Will be None if not present
                    V_H2O = products_dict.get('WATER VAPOR')
                    V_N2 = products_dict.get('NITROGEN')
                    
                    # Calculate yields if V_ variables are not None
                    try:
                        if V_SOOT is not None: params['soot_yield'] = str(round(V_SOOT * self.W_SOOT / molar_mass * 9500.0, 6))
                        if V_CO2 is not None: params['co2_yield'] = str(round(V_CO2 * self.W_CO2 / molar_mass, 6))
                        if V_CO is not None: params['co_yield'] = str(round(V_CO * self.W_CO / molar_mass, 6))
                        if V_HCl is not None: # Only calculate if HCl was present
                             params['hcl_yield'] = str(round(V_HCl * self.W_HCl / molar_mass, 6))
                        else: # Explicitly set to 0 if HCl was not in PRODUCTS
                             params['hcl_yield'] = "0.0"
                             
                        # Calculate O2 consumption from N2 if possible
                        if V_N2 is not None:
                            V_O2 = V_N2 / 3.7619
                            params['o2_consumption'] = str(round(V_O2 * self.W_O2 / molar_mass, 6))
                        # else: Attempt to calculate from NU values later
                            
                    except (ValueError, TypeError, ZeroDivisionError) as e:
                        self.statusBar.showMessage(f"Warning: Error calculating yields from PRODUCTS - {e}")
                else:
                     self.statusBar.showMessage("Warning: Mismatch between count, IDs, and VFs in PRODUCTS line.")
            
            # Attempt to get O2 consumption from REAC NU values if not found from PRODUCTS
            if 'o2_consumption' not in params:
                nu_match = re.search(r'&REAC.*?NU\s*\(\s*1\s*:\s*3\s*\)\s*=\s*-1\s*,\s*([\-\d\.]+)', fds_content, re.DOTALL | re.IGNORECASE)
                if nu_match:
                    try:
                        mass_reactants = float(nu_match.group(1))
                        # mass_reactants = -(1 + V_O2 * (1 + 3.7619 * (W_N2/W_O2)))
                        V_O2 = -1 * (mass_reactants + 1) / (1 + 3.7619 * (self.W_N2/self.W_O2))
                        params['o2_consumption'] = str(round(V_O2 * self.W_O2 / molar_mass, 6))
                    except (ValueError, TypeError, ZeroDivisionError) as e:
                         self.statusBar.showMessage(f"Warning: Could not parse/calculate O2 from REAC NU values - {e}")

            # Default any missing yields (especially HCl if PRODUCTS wasn't parsed)
            if 'hcl_yield' not in params: 
                 params['hcl_yield'] = "0.0"
            # Add defaults for others if needed, although they should ideally come from PRODUCTS
            # if 'soot_yield' not in params: params['soot_yield'] = "0.0" # Or handle as error?
            # ... etc for co2, co

            # Обновить поля ввода с извлеченными/установленными по умолчанию данными
            updated_params = False
            for param, value in params.items():
                if param in self.inputs:
                    self.inputs[param].setText(value)
                    updated_params = True
            
            # Найти и извлечь оригинальный блок SPEC/REAC из файла
            original_reac_block = ""
            try:
                # Найти все релевантные строки SPEC и REAC
                spec_pattern = r"&SPEC ID='(?:OXYGEN|NITROGEN|CARBON DIOXIDE|CARBON MONOXIDE|HYDROGEN CHLORIDE|WATER VAPOR|SOOT|AIR|PRODUCTS|{})'.*?/\n".format(re.escape(self.fuel_id))
                reac_pattern = r'&REAC.*?/\n'
                
                all_matches = []
                for pattern in [spec_pattern, reac_pattern]:
                    all_matches.extend(list(re.finditer(pattern, fds_content, re.DOTALL | re.IGNORECASE)))
                
                if all_matches:
                    all_matches.sort(key=lambda m: m.start())
                    start_pos = all_matches[0].start()
                    end_pos = all_matches[-1].end()
                    original_reac_block = fds_content[start_pos:end_pos].strip()
                else:
                     original_reac_block = "# Не удалось извлечь оригинальный блок SPEC/REAC."
                     
            except Exception as find_err:
                original_reac_block = f"# Ошибка при извлечении оригинального блока: {find_err}"

            if updated_params:
                # НЕ пересчитывать, просто показать оригинальный блок
                # self.calculate_parameters(silent=True) # УДАЛИТЬ ЭТУ СТРОКУ
                self.results_text.setText(original_reac_block)
                self.copy_button.setEnabled(bool(original_reac_block)) # Включить копирование, если блок извлечен
                self.save_fds_button.setEnabled(self.imported_file_path is not None) # Включить сохранение
                
                self.statusBar.showMessage("Параметры импортированы. Оригинальный блок REAC показан.")
                QMessageBox.information(self, "Успешный импорт", "Параметры успешно импортированы из файла FDS.\nОригинальный блок SPEC/REAC показан в области результатов.")
            else:
                self.results_text.clear() # Очистить результаты, если параметры не найдены
                self.copy_button.setEnabled(False)
                # Не отключать кнопку сохранения, так как файл был импортирован
                self.statusBar.showMessage("В файле FDS не найдены допустимые параметры REAC.")
                QMessageBox.warning(self, "Предупреждение при импорте", "В файле FDS не найдены допустимые параметры REAC.")
                
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при импорте файла FDS: {str(e)}")
            QMessageBox.critical(self, "Ошибка при импорте", 
                              f"Ошибка при импорте файла FDS:\n{str(e)}\n\n{traceback.format_exc()}")

    def save_to_fds_file(self):
        """Сохраняет рассчитанные REAC строки обратно в импортированный файл FDS"""
        try:
            if not self.imported_file_path or not self.results_text.toPlainText():
                self.statusBar.showMessage("Ошибка: Нет импортированного файла или рассчитанных результатов.")
                QMessageBox.warning(self, "Ошибка при сохранении", "Нет импортированного файла или рассчитанных результатов.")
                return

            # Читать исходный файл FDS
            with open(self.imported_file_path, 'r') as file:
                fds_content = file.read()
                
            # Получить новые REAC строки
            new_reac_lines = self.results_text.toPlainText()
            
            # Найти все существующие блоки SPEC и REAC в файле
            spec_reac_pattern = r'(&SPEC ID=\'OXYGEN\'.*?&REAC.*?/\n)'
            
            match = re.search(spec_reac_pattern, fds_content, re.DOTALL | re.IGNORECASE)
            if match:
                # Заменить совпавший блок с новыми REAC строками в том же положении
                modified_content = fds_content[:match.start()] + new_reac_lines + fds_content[match.end():]
            else:
                # Если не найден существующий блок, найти отдельные строки SPEC и REAC
                # Создать шаблоны для сопоставления всех отдельных строк SPEC и REAC
                spec_pattern = r'&SPEC ID=\'(?:OXYGEN|NITROGEN|CARBON DIOXIDE|CARBON MONOXIDE|HYDROGEN CHLORIDE|WATER VAPOR|SOOT|Fuel|AIR|PRODUCTS)\'.*?/\n'
                reac_pattern = r'&REAC.*?/\n'
                
                # Найти все вхождения
                spec_matches = list(re.finditer(spec_pattern, fds_content, re.DOTALL | re.IGNORECASE))
                reac_matches = list(re.finditer(reac_pattern, fds_content, re.DOTALL | re.IGNORECASE))
                
                if spec_matches or reac_matches:
                    # Получить все совпадения и отсортировать по их начальным позициям
                    all_matches = spec_matches + reac_matches
                    all_matches.sort(key=lambda x: x.start())
                    
                    if all_matches:
                        # Получить начальную позицию первого совпадения и конечную позицию последнего совпадения
                        start_pos = all_matches[0].start()
                        end_pos = all_matches[-1].end()
                        
                        # Заменить все совпадения с новым содержимым
                        modified_content = fds_content[:start_pos] + new_reac_lines + fds_content[end_pos:]
                    else:
                        # Не найдены совпадения, добавить в начало
                        modified_content = new_reac_lines + "\n" + fds_content
                else:
                    # Не найдены существующие строки, добавить после &HEAD или &MESH или в начало
                    insert_after_patterns = [r'(&HEAD.*?/\n)', r'(&MESH.*?/\n)']
                    insertion_point = 0
                    
                    for p in insert_after_patterns:
                        match = re.search(p, fds_content, re.DOTALL | re.IGNORECASE)
                        if match:
                            insertion_point = match.end()
                            break
                    
                    # Вставить новые REAC строки
                    modified_content = fds_content[:insertion_point] + "\n" + new_reac_lines + "\n" + fds_content[insertion_point:]
            
            # Спросить пользователя, где сохранить измененный файл
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить измененный файл FDS", "", "FDS файлы (*.fds);;Все файлы (*)"
            )
            
            if not save_path:
                return  # User canceled
                
            # Если нет расширения, добавить .fds
            if not save_path.lower().endswith('.fds'):
                save_path += '.fds'
                
            # Сохранить измененное содержимое
            with open(save_path, 'w') as file:
                file.write(modified_content)
                
            # Визуальная обратная связь
            self.statusBar.showMessage(f"Файл FDS успешно сохранен в: {save_path}")
            
            # Подсветка кнопки сохранения на короткое время
            orig_style = self.save_fds_button.styleSheet()
            self.save_fds_button.setStyleSheet("""
                background-color: #4ade80;
                color: #064e3b;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                min-width: 120px;
            """)
            
            # Reset after a delay
            QApplication.processEvents()
            import time
            time.sleep(0.3)
            self.save_fds_button.setStyleSheet(orig_style)
            
            QMessageBox.information(self, "Успешное сохранение", f"Измененный файл FDS успешно сохранен в:\n{save_path}")
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при сохранении файла FDS: {str(e)}")
            QMessageBox.critical(self, "Ошибка при сохранении", 
                              f"Ошибка при сохранении файла FDS:\n{str(e)}\n\n{traceback.format_exc()}")


def main():
    try:
        app = QApplication(sys.argv)
        window = FDSReacCalculator()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        print(traceback.format_exc())
        QMessageBox.critical(None, "Ошибка", 
                          f"Произошла ошибка:\n{str(e)}\n\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
