# PyAniParser

PyAniParser 是一个用于解析动画文件名的库，专门设计用于识别和提取动画文件名中的关键信息。

## 功能特点

- 支持多个字幕组/压制组的命名规则解析
- 内置多个常用字幕组的解析支持
- 支持批量文件解析

## 安装

```bash
pip install pyaniparser
```

## 使用方法

基本使用

```python
from pyaniparser import AniParser
# 单个title
parser = AniParser()
result = parser.parse("你的动画文件名.mp4")
print(result.title)
# 多个title
items = list(parser.parse_batch(["文件1.mp4", "文件2.mp4"]))
for result in items :
    print(result.title)
```

### 获取支持的字幕组列表

```python
parser = AniParser()
groups = parser.get_translation_parser_list()
```

## 内置解析器支持

目前支持以下字幕组/压制组的命名规则(按字典顺序)，完整支持的小组列表请见：[详细列表](https://github.com/banned2054/Banned.AniParser/blob/master/Docs/SupportedGroups.md)

- 北宇治字幕组
- 喵萌奶茶屋
- 桜都字幕组
- ANi
- jsum
- Kirara Fantasia
- Vcb-Studio

## 许可证

本项目采用 Apache-2.0 许可证。详情请参见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如果你在使用过程中遇到任何问题，请创建 Issue。