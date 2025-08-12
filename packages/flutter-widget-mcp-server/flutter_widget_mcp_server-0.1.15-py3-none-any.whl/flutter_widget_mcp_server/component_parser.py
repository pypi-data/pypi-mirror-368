"""
Description: Flutter Widget组件库 - Markdown单组件文档解析器
"""

import re
from typing import List, Optional
from .models import (
    FlutterWidgetComponent, ComponentProperty, ComponentEvent,
    ComponentExample, ComponentFAQ, ComponentMethod
)

def get_code_examples(md: str) -> List[ComponentExample]:
    """
    从Markdown文档中提取代码示例部分的所有示例代码
    
    Args:
        md: Markdown文档内容
        
    Returns:
        List[ComponentExample]: 包含示例标题和代码的列表
    """
    examples = []
    lines = md.splitlines()
    in_section = False
    current_section = []
    
    # 提取代码示例部分
    for line in lines:
        if line.strip() == "## 代码示例":
            in_section = True
            continue
        elif line.startswith("## ") and in_section:
            break
        
        if in_section:
            current_section.append(line)
    
    # 解析代码示例
    if current_section:
        code_section = '\n'.join(current_section)
        for match in re.finditer(r"### ([^\n]+)\n+```(\w+)?\n(.*?)```", code_section, re.DOTALL):
            title, language, code = match.groups()
            examples.append(ComponentExample(
                title=title.strip(),
                code=code.strip() if code else ""
            ))
    
    return examples

def extract_faq(md: str) -> List[ComponentFAQ]:
    """
    提取FAQ问答
    
    Args:
        md: Markdown文档内容
        
    Returns:
        List[ComponentFAQ]: FAQ问答列表
    """
    faqs = []
    lines = md.splitlines()
    in_section = False
    current_section = []
    
    # 提取FAQ部分
    for line in lines:
        if line.strip() == "## 常见问题":
            in_section = True
            continue
        elif line.startswith("## ") and in_section:
            break
        
        if in_section:
            current_section.append(line)
    
    # 解析FAQ
    if current_section:
        faq_section = '\n'.join(current_section)
        for match in re.finditer(r"###\s*Q[:：]\s*(.+?)\nA[:：]\s*(.+?)(?=\n###|\Z)", faq_section, re.DOTALL):
            question, answer = match.groups()
            faqs.append(ComponentFAQ(
                question=question.strip(),
                answer=answer.strip()
            ))
    
    return faqs

def extract_section(md: str, title: str) -> Optional[str]:
    """
    提取指定title下的内容，不包含下一个同级标题的部分
    """
    pattern = rf"^##+\s*{re.escape(title)}\s*\n(.*?)(?=^##+|\Z)"
    match = re.search(pattern, md, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_table(md: str) -> List[List[str]]:
    """
    提取markdown表格，返回二维数组
    """
    lines = [line.strip() for line in md.splitlines() if line.strip()]
    if not lines or '|' not in lines[0]:
        return []
    header = lines[0]
    sep_idx = 1 if len(lines) > 1 and set(lines[1]) <= set('-|:') else 0
    rows = []
    for line in lines[sep_idx+1:]:
        if '|' in line:
            rows.append([cell.strip() for cell in line.split('|')[1:-1]])
    return rows

def extract_code_blocks(md: str) -> List[str]:
    """
    提取所有dart代码块
    """
    return re.findall(r"```dart(.*?)```", md, re.DOTALL)

def extract_methods(md: str) -> List[ComponentMethod]:
    """
    提取方法信息
    """
    method_section = extract_section(md, "方法")
    if not method_section:
        return []
    
    methods = []
    method_rows = extract_table(method_section)
    for row in method_rows:
        if len(row) >= 4:
            name, description, params, return_type = row[:4]
            parameters = [param.strip() for param in params.split(',') if param.strip()]
            methods.append(ComponentMethod(
                name=name,
                description=description,
                parameters=parameters,
                return_type=return_type
            ))
    return methods

def parse_component_markdown(md_path: str) -> FlutterWidgetComponent:
    """
    解析md文件为FlutterWidgetComponent对象
    """
    with open(md_path, encoding="utf-8") as f:
        md = f.read()

    # 简单正则提取基本信息
    name_match = re.search(r"#\s*([^\n<]+)", md)
    id_match = re.search(r"<([A-Za-z0-9_]+)>", md)
    cat_match = re.search(r"- \*\*分类\*\*:\s*([^\n]+)", md)
    maint_match = re.search(r"- \*\*维护者\*\*:\s*([^\n]*)", md)
    stab_match = re.search(r"- \*\*稳定性\*\*:\s*([^\n]*)", md)
    desc_match = re.search(r"## 简介\n(.*?)(?=\n##|\Z)", md, re.DOTALL)
    preview_match = re.search(r"!\[.*?\]\((.*?)\)", md)
    scenarios = []
    scn_section = extract_section(md, "适用场景")
    if scn_section:
        scenarios = [line.lstrip("-•* ").strip() for line in scn_section.splitlines() if line.strip()]
    import_match = re.search(r"```dart\nimport[^\n]*\n```", md)
    usage_block = re.search(r"## 基础用法.*?```dart(.*?)```", md, re.DOTALL)
    usage = usage_block.group(1).strip() if usage_block else None

    # 属性表
    prop_section = extract_section(md, "属性")
    properties = []
    if prop_section:
        prop_rows = extract_table(prop_section)
        for row in prop_rows:
            if len(row) >= 5:
                properties.append(ComponentProperty(
                    name=row[0], description=row[1], type=row[2],
                    default=row[3] if row[3] != "-" else None,
                    required=row[4] == "是"
                ))

    # 事件表
    evt_section = extract_section(md, "事件")
    events = []
    if evt_section:
        evt_rows = extract_table(evt_section)
        for row in evt_rows:
            if len(row) >= 3:
                events.append(ComponentEvent(
                    name=row[0], description=row[1], params=row[2]
                ))

    # 示例代码
    examples = get_code_examples(md)
    # FAQ
    faqs = extract_faq(md)
    # 源码/示例路径
    src_match = re.search(r"- \[源码路径\]\(([^)]+)\)", md)
    demo_match = re.search(r"- \[示例代码\]\(([^)]+)\)", md)

    # 提取方法信息
    methods = extract_methods(md)

    return FlutterWidgetComponent(
        id=id_match.group(1) if id_match else (name_match.group(1).strip() if name_match else ""),
        name=name_match.group(1).strip() if name_match else "",
        category=cat_match.group(1).strip() if cat_match else "",
        maintainer=maint_match.group(1).strip() if maint_match else None,
        stability=stab_match.group(1).strip() if stab_match else None,
        description=desc_match.group(1).strip() if desc_match else "",
        preview=preview_match.group(1) if preview_match else None,
        scenarios=scenarios,
        import_code=import_match.group(0) if import_match else None,
        basic_usage=usage,
        properties=properties,
        events=events,
        examples=examples,
        faq=faqs,
        source_path=src_match.group(1) if src_match else None,
        demo_path=demo_match.group(1) if demo_match else None,
        methods=methods
    )
