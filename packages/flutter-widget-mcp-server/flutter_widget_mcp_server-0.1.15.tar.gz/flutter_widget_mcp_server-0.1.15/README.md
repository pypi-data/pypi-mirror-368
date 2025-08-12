# Flutter Widget MCP Server

Flutter Widget MCP Server 是一个用于 Flutter Widget 组件库的 Model Context Protocol (MCP) 服务器。它提供了一个强大的 API 来查询和搜索 Flutter 组件的详细信息。

## 特性

- 组件查询：获取特定组件的详细信息
- 组件列表：获取所有可用组件的列表
- 组件搜索：根据关键词搜索组件
- 支持部分匹配和不区分大小写的查询

## PYPI安装

推荐使用最新版本的pip来安装Flutter Widget MCP Server。

> https://pypi.org/project/flutter-widget-mcp-server/

首先，更新pip：

```
python -m pip install --upgrade pip
```

然后，使用pip安装Flutter Widget MCP Server：

```
pip install flutter-widget-mcp-server
```


## 源码安装

1. 确保你已经安装了 Python 3.7+。
2. 安装依赖：

```
pip install -r requirements.txt
```


## 生成组件数据

在运行服务器之前，需要先生成组件数据：

> 定位到 mcp/flutter_widget_mcp_server 目录

```
 python -m flutter_widget_mcp_server.gen_components_json
```

## 运行服务器

> 定位到 mcp/flutter_widget_mcp_server 目录

```
python -m flutter_widget_mcp_server.main
```

服务器将在 http://0.0.0.0:${port} 上运行。


## 注意事项

- 组件数据存储在 `mcp/flutter_widget_mcp_server/flutter_widget_mcp_server/components.json` 文件中。
- 如果修改了组件文档，需要重新运行生成脚本来更新组件数据。
