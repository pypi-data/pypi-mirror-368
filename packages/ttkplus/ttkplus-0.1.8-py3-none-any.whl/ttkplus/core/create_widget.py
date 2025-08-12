from tkinter import Widget

from ttkbootstrap import Label, Button, Entry, Canvas, Checkbutton, Combobox, DateEntry, LabelFrame, Frame, Menubutton, \
    Meter, Notebook, Progressbar, Radiobutton, Scale, Spinbox, Text, Treeview

from ttkplus.core.model import TkLayout
from ttkplus.logger import log


class CreateWidget:

    def __init__(self, parent, model: TkLayout):
        self.model = model
        self.parent = parent

    def make(self) -> Widget:
        widget_type = self.model.type
        widget_type = widget_type.replace('-', '_')
        if not hasattr(self, f"_{widget_type}"):
            log.info('GenerateWidgets：组件不存在')
            return Label(self.parent, text=widget_type)
        func = getattr(self, f"_{widget_type}")
        log.info(f'widget model: {self.model}')
        return func()

    def _ttk_label(self) -> Label:
        wgt = Label(self.parent, text=self.model.text)
        return wgt

    def _ttk_button(self) -> Button:
        wgt = Button(self.parent, text=self.model.text)
        return wgt

    def _ttk_entry(self) -> Entry:
        wgt = Entry(self.parent)
        return wgt

    def _ttk_canvas(self) -> Canvas:
        wgt = Canvas(self.parent)
        return wgt

    def _ttk_checkbutton(self) -> Checkbutton:
        wgt = Checkbutton(self.parent)
        return wgt

    def _ttk_combobox(self) -> Combobox:
        wgt = Combobox(self.parent)
        return wgt

    def _ttk_date_entry(self) -> DateEntry:
        wgt = DateEntry(self.parent)
        return wgt

    def _ttk_label_frame(self) -> LabelFrame:
        wgt = LabelFrame(self.parent, text=self.model.text)
        return wgt

    def _ttk_frame(self) -> Frame:
        wgt = Frame(self.parent)
        return wgt

    def _ttk_menubutton(self) -> Menubutton:
        wgt = Menubutton(self.parent)
        return wgt

    def _ttk_meter(self) -> Meter:
        wgt = Meter(self.parent)
        return wgt

    def _ttk_notebook(self) -> Notebook:
        wgt = Notebook(self.parent)
        return wgt

    def _ttk_progressbar(self) -> Progressbar:
        wgt = Progressbar(self.parent)
        return wgt

    def _ttk_radiobutton(self) -> Radiobutton:
        wgt = Radiobutton(self.parent)
        return wgt

    def _ttk_scale(self) -> Scale:
        wgt = Scale(self.parent)
        return wgt

    def _ttk_spinbox(self) -> Spinbox:
        wgt = Spinbox(self.parent)
        return wgt

    def _ttk_text(self) -> Text:
        wgt = Text(self.parent)
        return wgt

    def _ttk_treeview(self) -> Treeview:
        wgt = Treeview(self.parent)
        return wgt
