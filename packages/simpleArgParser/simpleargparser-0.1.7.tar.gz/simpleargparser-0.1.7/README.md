# SimpleArgParser

## Installation

```
pip install simpleArgParser
```

## Introduction

This is a simple command line argument parser encapsulated based on Python dataclasses and type hints, supporting:
- Defining arguments using classes (required, optional, and arguments with default values)
- Nested dataclasses, with argument names separated by dots
- JSON configuration file loading (priority: command line > code input > JSON config > default value)
- List type arguments (supports comma separation)
- Enum types (pass in the name of the enum member, and display options in the help)
- Custom post-processing (post_process method)

Detailed introduction is coming soon. Please also refer to `examples/example.py`.

## args order

重新排列一下参数显示的顺序：

1、首先显示required args
2、优先短的separate显示，就是xxx比xxx.xxx优先级高，xxxx.xxxx 比xxx.xxx.xxx优先级高
3、最后按照字母序排列