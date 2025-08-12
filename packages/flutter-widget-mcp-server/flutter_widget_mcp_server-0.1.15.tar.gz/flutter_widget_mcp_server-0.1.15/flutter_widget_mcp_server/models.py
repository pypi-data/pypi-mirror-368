"""
Description: Flutter Widget 组件库 MCP Server - 元数据Pydantic模型定义
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class ComponentMethod(BaseModel):
    """
    组件方法模型
    参数说明：
        - name: 方法名
        - description: 方法说明
        - parameters: 参数列表
        - return_type: 返回值类型
    """
    name: str = Field(..., description="方法名")
    description: str = Field(..., description="方法说明")
    parameters: List[str] = Field(default_factory=list, description="参数列表")
    return_type: str = Field(..., description="返回值类型")

class ComponentProperty(BaseModel):
    """
    组件属性模型
    参数说明：
        - name: 属性名
        - description: 属性说明
        - type: 属性类型
        - default: 默认值
        - required: 是否必填
    """
    name: str = Field(..., description="属性名")
    description: str = Field(..., description="属性说明")
    type: str = Field(..., description="属性类型")
    default: Optional[str] = Field(None, description="默认值")
    required: bool = Field(..., description="是否必填")

class ComponentEvent(BaseModel):
    """
    组件事件模型
    参数说明：
        - name: 事件名
        - description: 事件说明
        - params: 回调参数
    """
    name: str = Field(..., description="事件名")
    description: str = Field(..., description="事件说明")
    params: Optional[str] = Field(None, description="回调参数说明")

class ComponentExample(BaseModel):
    """
    组件代码示例模型
    参数说明：
        - title: 示例标题
        - code: 示例代码
        - description: 示例说明
    """
    title: str = Field(..., description="示例标题")
    code: str = Field(..., description="示例代码")
    description: Optional[str] = Field(None, description="示例说明")

class ComponentFAQ(BaseModel):
    """
    组件常见问题模型
    参数说明：
        - question: 常见问题
        - answer: 解答
    """
    question: str = Field(..., description="常见问题")
    answer: str = Field(..., description="解答")


class FlutterWidgetComponent(BaseModel):
    """
    Flutter Widget 组件元数据模型
    参数说明：
        - id: 组件唯一标识
        - name: 组件名称
        - category: 组件分类
        - maintainer: 维护者
        - stability: 稳定性
        - description: 简介
        - preview: 预览图URL
        - scenarios: 适用场景
        - import_code: 导入方式
        - basic_usage: 基础用法代码
        - properties: 属性列表
        - events: 事件列表
        - examples: 代码示例
        - faq: 常见问题
        - source_path: 源码路径
        - demo_path: 示例代码路径
    """
    id: str = Field(..., description="组件唯一标识")
    name: str = Field(..., description="组件名称")
    category: str = Field(..., description="组件分类")
    maintainer: Optional[str] = Field(None, description="维护者")
    stability: Optional[str] = Field(None, description="稳定性")
    description: str = Field(..., description="组件简介")
    preview: Optional[str] = Field(None, description="预览图URL")
    scenarios: List[str] = Field(default_factory=list, description="适用场景")
    import_code: Optional[str] = Field(None, description="导入方式")
    basic_usage: Optional[str] = Field(None, description="基础用法代码")
    properties: List[ComponentProperty] = Field(default_factory=list, description="属性列表")
    events: List[ComponentEvent] = Field(default_factory=list, description="事件列表")
    examples: List[ComponentExample] = Field(default_factory=list, description="代码示例")
    faq: List[ComponentFAQ] = Field(default_factory=list, description="常见问题")
    source_path: Optional[str] = Field(None, description="源码路径")
    demo_path: Optional[str] = Field(None, description="示例代码路径")
    methods: List[ComponentMethod] = Field(default_factory=list, description="方法列表")
