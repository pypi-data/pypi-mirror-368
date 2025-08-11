# gx-toolkit-datalab

`gx-toolkit-datalab`，全称**Gx Company Development Toolkit - DataLab Module** ，是**泰富共享**开发的基于Python和Rust的数据分析与数据处理工具。

作为`gx-toolkit`依赖的子模块之一，若要使用`gx-toolkit`的数据分析与数据处理功能，请安装此包。

## 如何安装

`gx-toolkit-datalab`目前有两个版本，分为**正式版**和**测试版**。

- **正式版**：发布在**PyPI**的版本，较为稳定
- **测试版**：发布在**TestPyPI**的版本，更新快

**正式版**安装方式：

```
pip install gxkit-datalab
```

**测试版**安装方式：

```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.tuna.tsinghua.edu.cn/simple gxkit-datalab
```

测试版在导入时需注意输入正确的**URL**：https://test.pypi.org/simple/

**TestPyPI**上部分库**代码不全或没有最新版**，没有编译好的`.whl`文件（**PyPI**则不会有此问题），因此有部分依赖冲突。需要增加`extra-index-url`帮助用户获取最新版依赖库。

## 功能模块

- `client` 数据库客户端，包含Mysql、ClickHouse以及IoTDB

## 依赖项

- `pandas` 
- `pvlib`

## 快速入门

作者暂时懒得编写。请直接联系作者（shaojy@sunburst.com.cn）。

## 版本与许可证

当前的最新版本：`0.1.0`

许可证： `Apache License 2.0` 