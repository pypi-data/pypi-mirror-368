from typing import Optional, Dict, List

from pydantic import BaseModel


class GridConfigItem(BaseModel):
    size: int  # 宽高
    weight: int  # 权重


class GridConfig(BaseModel):
    colItems: List[GridConfigItem]
    rowItems: List[GridConfigItem]


class TkLayout(BaseModel):
    gridConfig: Optional[GridConfig] = None
    elements: Optional[Dict[str, 'TkLayout']] = None
    type: str
    key: str
    bootStyle: Optional[str] = None
    bootWidgetType: Optional[str] = None
    text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fullWidth: Optional[bool] = None
    fullHeight: Optional[bool] = None
    state: Optional[str] = None
    sticky_list: Optional[List[str]] = None
    margin: Optional[List[int]] = None
    padding: Optional[List[int]] = None
    tab_name: Optional[str] = None
    tab_index: Optional[int] = None


class TkWindow(BaseModel):
    title: str
    width: int
    height: int
    minWidth: int
    minHeight: int
    theme: str
    isChildWindow: bool


class HelperInfo(BaseModel):
    version: str
    website: str
    qqGroup: str
    name: str


class TkHelperModel(BaseModel):
    layout: TkLayout
    window: TkWindow
    helperInfo: HelperInfo


# 更新前向引用
TkLayout.update_forward_refs()
