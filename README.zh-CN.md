# 富士固件解密／解包工具

[English README](README.md) · [格式说明](docs/FORMAT.md) · [实包验证](docs/VALIDATION.md)

这是一套离线、只读的富士 DAT 固件分析工具，支持 DAT 容器解析、XOR `0xFF` 去混淆和带段头的 FFLZ 数据解压。运行时只依赖 Python 标准库，不连接相机、不使用 USB，也不执行刷机。

## 功能

- 读取 DAT 格式版本、机型代码、固件版本和 payload 偏移。
- 生成 DAT payload 的 XOR `0xFF` 视图。
- 扫描 FFLZ 段头，在严格输入／输出边界内解压数据。
- 保存解码段、SHA-256 和机器可读的 `manifest.json`。
- 同时提供 Python API 与 `fujitools` 命令行。

## 已实测固件

| 机型 | 固件版本 | 成功解码的 FFLZ 段 |
| --- | --- | ---: |
| 富士 X-T4 | 2.12 | 4/4 |
| 富士 X100V | 3.01 | 2/2 |
| 富士 X-T5 | 4.31 | 4/4 |

这证明当前工具可以跨机型处理已观察到的格式，但不代表支持所有富士相机或所有 DAT 世代。来源、哈希和输出统计见 [验证记录](docs/VALIDATION.md)。

## 安装

需要 Python 3.10 或更新版本：

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

开发模式：

```sh
python -m pip install -e .
```

也可以不安装，直接在源码目录运行：

```sh
PYTHONPATH=src python3 -m fujitools --help
```

## 使用

读取固件信息：

```sh
fujitools info FWUP0024.DAT
fujitools info FWUP0024.DAT --json
```

只生成 XOR 视图：

```sh
fujitools xview FWUP0024.DAT -o firmware.xor.bin
```

生成 XOR 视图并解码全部可识别的 FFLZ 段：

```sh
fujitools unpack FWUP0024.DAT -o out/xt4-2.12
```

自动化任务可加 `--strict`：没有成功解码段，或任何段头候选解码失败时返回非零状态。

输出结构：

```text
out/xt4-2.12/
├── firmware.xor.bin
├── manifest.json
└── sections/
    ├── 00260060.bin
    └── ...
```

本仓库不分发富士固件。请从富士官方支持页面自行获取，并遵守适用条款。

## 边界

- 这里所称“解密”是逆转简单的 XOR `0xFF` 混淆，并进行 FFLZ 解压。
- XOR 视图会对整个 payload 取反，因此原本已经明文存储的资源区在该视图中反而会反转。
- 当前 FFLZ 解码器针对 [格式说明](docs/FORMAT.md) 中的 20 字节段头；遇到未知格式会报告，不会伪造成功结果。
- 本项目不绕过固件签名、不重打包、不写相机内存、不刷机。
- FFLZ 段成功解码不等于所有内嵌资源和文件系统都已完成语义解包。

## 测试与贡献

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

测试只使用合成数据，不需要专有固件或相机。贡献规则见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

采用 [MIT 许可证](LICENSE)。富士固件及相关商标归原权利人所有；本项目是独立的互操作研究工具，不是富士官方产品。
