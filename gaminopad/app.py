import os
import time
import PySimpleGUI as sg
from gaminopad import strings
from gaminopad.state_register import StateRegister


class Font:
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def get(self):
        return self.name, self.size


class Notepad:

    def __init__(self, config):
        self.config = config
        self.app_name = config['app_name']
        self.w_width = 90
        self.w_height = 25
        self.TXT_BODY = '_BODY_'
        self.filename = None
        self.tmp_filename = config['temp_filename']
        self.window = None
        self.body_font = Font("Consolas", 12)
        self.icon_path = config['icon_path']
        self.tmp_path = config['temp_filepath']
        self.default_ext = config['default_extension']
        self.layout = self._build_layout()
        self._create_tmp_path()
        self.save_state_interval = 0.5
        self.state_reg = StateRegister(config['state_reg_memory_len'])
        self.curr_text = ''

    def _create_tmp_path(self):
        if not os.path.isdir(self.tmp_path):
            os.mkdir(self.tmp_path)

    def _build_layout(self):
        menu_layout = [[strings.FILE_MENU, [strings.FILE_NEW,
                                            strings.FILE_OPEN,
                                            strings.FILE_SAVE,
                                            strings.FILE_SAVE_AS,
                                            strings.EXIT]],
                       [strings.EDIT_MENU, [strings.UNDO,
                                            strings.REDO]]]
        layout = [[sg.MenuBar(menu_layout)],
                  [sg.Multiline(font=self.body_font.get(),
                                size=(self.w_width, self.w_height),
                                key=self.TXT_BODY)]]
        return layout

    def start(self):
        self.window = sg.Window(
            self.app_name,
            layout=self.layout,
            margins=(0, 0),
            resizable=True,
            return_keyboard_events=True,
            icon=self.icon_path)
        self.window.read(timeout=1)
        self.read_tmp_file()
        self.window[self.TXT_BODY].expand(expand_x=True, expand_y=True)
        self._main_loop()

    def _main_loop(self):
        save_state_t0 = time.time()
        self._save_state()

        while True:
            event, values = self.window.read()

            if values and self.TXT_BODY in values:
                self.curr_text = values.get(self.TXT_BODY).strip()

            if event in (None, strings.EXIT):
                self.save_tmp_file()
                self.window.close()
                break

            if time.time() - save_state_t0 >= self.save_state_interval:
                save_state_t0 = time.time()
                self._save_state()
                self.save_tmp_file()

            if event in (strings.FILE_NEW, strings.CTRL_N):
                self.new_file()
            elif event in (strings.FILE_OPEN, strings.CTRL_O):
                self.open_file()
            elif event in (strings.FILE_SAVE, strings.CTRL_S):
                self.save_file()
            elif event == strings.FILE_SAVE_AS:
                self.save_file_as()
            elif event in (strings.UNDO, strings.CTRL_Z):
                self.undo()
            elif event in (strings.REDO, strings.CTRL_Y):
                self.redo()

    def _save_state(self):
        self.state_reg.push_state(self.curr_text)

    def undo(self):
        undo_text = self.state_reg.undo()
        if undo_text is not None:
            self._update_body(undo_text)

    def redo(self):
        redo_text = self.state_reg.redo()
        if redo_text is not None:
            self._update_body(redo_text)

    def _confirm_loss_of_data(self):
        if self.filename is None and self.curr_text != '':
            answer = sg.Popup(strings.CONFIRMATION_TEXT, button_type=5,
                              custom_text=(strings.OK, strings.CANCEL))
            return answer not in (None, strings.CANCEL)
        else:
            return True

    def new_file(self):
        if self._confirm_loss_of_data():
            self._update_body('')
            self.state_reg.reset()
            self._save_state()
            self.filename = None

    def _update_body(self, text):
        self.curr_text = text
        self.window[self.TXT_BODY].update(value=text)

    def open_file(self):
        if self._confirm_loss_of_data():
            try:
                self.filename = sg.popup_get_file(strings.OPEN_FILE, no_window=True)
            except:
                return

            if self.filename not in (None, '') and not isinstance(
                    self.filename,
                    tuple):
                with open(self.filename, 'r') as f:
                    self._update_body(f.read())
                    self.state_reg.reset()
                    self._save_state()

    def save_tmp_file(self):
        with open(self.tmp_path + self.tmp_filename, 'w') as f:
            f.write(self.curr_text)

    def read_tmp_file(self):
        try:
            with open(self.tmp_path + self.tmp_filename, 'r') as f:
                self._update_body(f.read())
        except FileNotFoundError:
            pass

    def save_file(self):
        if self.filename not in (None, ''):
            with open(self.filename, 'w') as f:
                f.write(self.curr_text)
        else:
            self.save_file_as()

    def save_file_as(self):
        try:
            save_filename = sg.popup_get_file(
                strings.SAVE_FILE,
                save_as=True,
                no_window=True,
                default_extension=self.default_ext[1],
                file_types=(self.default_ext,))
        except:
            return
        if save_filename not in (None, '') and not isinstance(save_filename,
                                                              tuple):
            with open(save_filename, 'w') as f:
                self.filename = save_filename
                f.write(self.curr_text)
