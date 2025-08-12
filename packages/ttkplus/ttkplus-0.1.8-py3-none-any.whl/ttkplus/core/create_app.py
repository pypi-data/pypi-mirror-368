from tkinter import Widget

from ttkbootstrap import Style
from ttkbootstrap import Window

from ttkplus.core.model import TkHelperModel
from ttkplus.core.render import Render

GRID_BOX_STYLE = 'grid_box.TFrame'


class CreateApp:
    def __init__(self, model: TkHelperModel):
        self._widgets = dict()
        self._model = model
        self._root = self.__create_window()
        self.__render = Render()
        self.__build()

    def __build(self):
        self.__create_style()
        self._widgets = self.__render.recursion_create(self._model.layout, self._root)

    def run(self):
        self._root.mainloop()

    def get_widget(self, key) -> Widget:
        return self._widgets[key]

    def __create_window(self):
        win_model = self._model.window
        root = Window(themename=win_model.theme, title=win_model.title, size=(win_model.width, win_model.height))
        root.place_window_center()
        return root

    def __create_style(self):
        style = Style()
        style.configure(GRID_BOX_STYLE, bordercolor='purple', borderwidth=1, relief='solid', backgroundcolor="purple")
