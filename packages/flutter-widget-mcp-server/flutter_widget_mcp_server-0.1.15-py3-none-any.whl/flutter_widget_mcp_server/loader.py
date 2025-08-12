"""
Description: Flutter Widget组件库 - 只读本地JSON缓存检索（不再直接读取md）
"""

import json
import logging
from typing import List, Optional
from .models import FlutterWidgetComponent

logger = logging.getLogger("flutter_widget_mcp_server.ComponentRepository")

class ComponentRepository:
    """
    组件仓库，仅从本地JSON文件加载组件数据
    """
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.components: List[FlutterWidgetComponent] = []
        self.name_index = {}
        self.category_index = {}
        logger.info(f"Initializing ComponentRepository with {json_path}")
        self._load_all_components()

    def _load_all_components(self):
        """
        读取JSON文件并索引缓存
        """
        logger.info("Loading all components from JSON file")
        self.components.clear()
        self.name_index.clear()
        self.category_index.clear()
        try:
            with open(self.json_path, encoding="utf-8") as f:
                data = json.load(f)
            for d in data:
                comp = FlutterWidgetComponent(**d)
                self.components.append(comp)
                # 名称索引
                self.name_index[comp.name] = comp
                # 分类索引
                cat = comp.category
                if cat not in self.category_index:
                    self.category_index[cat] = []
                self.category_index[cat].append(comp)
            logger.info(f"Loaded {len(self.components)} components")
        except Exception as e:
            logger.error(f"Error loading components: {str(e)}", exc_info=True)

    def all(self) -> List[FlutterWidgetComponent]:
        """
        返回所有组件
        """
        logger.debug("Returning all components")
        return list(self.components)

    def get_by_name(self, name: str) -> Optional[FlutterWidgetComponent]:
        """
        根据组件名检索，支持部分匹配
        """
        logger.info(f"Searching for component: {name}")
        for component_name, component in self.name_index.items():
            if name.lower() in component_name.lower():
                logger.info(f"Component {name} found (matched: {component_name})")
                return component
        logger.warning(f"Component {name} not found")
        return None

    def list_by_category(self, category: str) -> List[FlutterWidgetComponent]:
        """
        按分类检索组件
        """
        logger.info(f"Listing components by category: {category}")
        components = list(self.category_index.get(category, []))
        logger.info(f"Found {len(components)} components in category {category}")
        return components

    def search(self, keyword: str, category: Optional[str]=None) -> List[FlutterWidgetComponent]:
        """
        支持关键词和可选分类模糊检索
        """
        logger.info(f"Searching for keyword: {keyword}, category: {category}")
        result = []
        comps = self.category_index.get(category, []) if category else self.components
        for comp in comps:
            if (keyword.lower() in comp.name.lower() or
                keyword.lower() in comp.description.lower()):
                result.append(comp)
        logger.info(f"Found {len(result)} components matching search criteria")
        return result

    def reload(self):
        """
        重新加载全部组件（支持热更新）
        """
        logger.info("Reloading all components")
        self._load_all_components()
