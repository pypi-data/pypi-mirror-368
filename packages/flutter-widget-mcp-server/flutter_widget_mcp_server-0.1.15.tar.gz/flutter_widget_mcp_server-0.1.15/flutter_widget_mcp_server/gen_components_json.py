"""
Description: 批量解析组件md文档，生成结构化JSON缓存文件供MCP Server使用
"""

import os
import sys
import json
from .component_parser import parse_component_markdown

def list_md_files(root_dir):
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def main():
    # 支持命令行参数指定目录和输出路径
    docs_root = sys.argv[1] if len(sys.argv) > 1 else "../../mcp/docs/components"
    out_json = sys.argv[2] if len(sys.argv) > 2 else "./flutter_widget_mcp_server/components.json"

    abs_docs_root = os.path.abspath(docs_root)
    abs_out_json = os.path.abspath(out_json)
    print(f"[INFO] 扫描目录: {abs_docs_root}")
    md_files = list_md_files(abs_docs_root)
    print(f"[INFO] 共找到 {len(md_files)} 个md文件")

    data = []
    for md_path in md_files:
        try:
            comp = parse_component_markdown(md_path)
            data.append(comp.model_dump())
        except Exception as e:
            print(f"[ERROR] 解析失败: {md_path}: {e}")

    with open(abs_out_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] 生成JSON：{abs_out_json}, 共导出{len(data)}个组件")

if __name__ == "__main__":
    main()
