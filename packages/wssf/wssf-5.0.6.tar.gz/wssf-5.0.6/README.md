# 文叔叔完整版工具 (Wenshushu Enhanced CLI Tool)

一个功能完整的文叔叔命令行工具，整合了断点续传、多文件下载、目录上传、用户登录、取件码、代理支持等所有功能。

## 环境管理

该项目支持两种依赖管理方式：现代化的 **uv** 和传统的 **pip**。

### 方式一：使用 uv（推荐）

uv 是新一代的 Python 包管理器，提供更快的包安装和更好的依赖解析。

#### 安装 uv
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 使用 uv 管理项目
```bash
# 同步依赖（自动创建虚拟环境并安装依赖）
uv sync

# 激活虚拟环境
# Windows
.venv\Scripts\activate

# Unix/Linux/macOS  
source .venv/bin/activate

# 运行项目
python wss.py -h

# 添加新的依赖
uv add package_name

# 移除依赖
uv remove package_name

# 显示当前依赖
uv pip list
```

### 方式二：使用 pip（传统方式）

#### 创建虚拟环境（推荐）
```bash
# 创建虚拟环境(conda也可)
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Unix/Linux/macOS
source venv/bin/activate
```

#### 安装依赖
```bash
# 从 requirements.txt 安装（如果存在）
pip install -r requirements.txt

# 或手动安装核心依赖
pip install requests base58 pycryptodomex

# 生成 requirements.txt
pip freeze > requirements.txt
```

### 项目依赖说明

根据 `pyproject.toml` 文件，项目的核心依赖包括：

- **requests** (>=2.32.4) - HTTP 请求库，用于与文叔叔 API 通信
- **base58** (>=2.1.1) - Base58 编码库，用于数据编码
- **pycryptodomex** (>=3.23.0) - 加密库，用于 DES 加密算法

项目要求 Python 版本 >= 3.13。

## wss.py 脚本功能详解

`wss.py` 是项目的主要脚本文件，集成了所有功能模块。以下是详细的功能说明：

### 核心功能概览

1. **文件上传** - 支持单文件和目录上传
2. **文件下载** - 支持单线程和多线程下载，包含断点续传
3. **用户管理** - 多账户登录、切换和管理
4. **取件码** - 自定义或随机生成取件码
5. **代理支持** - HTTP/HTTPS/SOCKS 代理
6. **多语言** - 中文/英文界面切换
7. **断点续传** - 支持下载中断后继续

### 命令行参数详解

#### 基本命令结构
```bash
python wss.py <命令> [目标] [选项]
```

#### 主要命令
| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `upload` | `u` | 上传文件或目录 | `python wss.py u file.txt` |
| `download` | `d` | 下载文件 | `python wss.py d "链接"` |
| `login` | - | 账户登录管理 | `python wss.py login` |
| `unlogin` | - | 退出当前账户 | `python wss.py unlogin` |

#### 功能选项
| 选项 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--help` | `-h` | 显示双语帮助信息 | `python wss.py -h` |
| `--en` | `-e` | 使用英文界面 | `python wss.py u file.txt -e` |
| `--login` | `-l` | 使用已登录账户 | `python wss.py u file.txt -l` |
| `--continue` | `-c` | 启用断点续传（仅下载） | `python wss.py d "链接" -c` |
| `--threads` | `-t` | 设置下载线程数(1-16) | `python wss.py d "链接" -t 8` |
| `--key` | `-k` | 设置4位取件码 | `python wss.py u file.txt -k 1234` |
| `--randomkey` | `-r` | 随机生成取件码 | `python wss.py u file.txt -r` |
| `--proxy` | `-p` | 设置代理服务器 | `python wss.py u file.txt -p http://proxy` |

### 详细功能说明

#### 1. 文件上传功能

##### 基本上传
```bash
# 上传单个文件
python wss.py upload file.txt
python wss.py u file.txt  # 使用别名

# 上传目录（自动压缩为 tar.gz）
python wss.py upload ./folder
python wss.py u ./folder
```

##### 高级上传选项
```bash
# 设置自定义取件码
python wss.py u file.txt -k 1234

# 随机生成取件码
python wss.py u file.txt -r

# 使用已登录账户上传（更大存储空间）
python wss.py u file.txt -l

# 通过代理上传
python wss.py u file.txt -p http://127.0.0.1:8080

# 英文界面上传
python wss.py u file.txt -e

# 组合多个选项
python wss.py u file.txt -l -r -p http://proxy -e
```

##### 上传功能特性
- **目录压缩**：自动将目录压缩为 tar.gz 格式
- **智能检测**：自动检测文件是否可以秒传
- **分块上传**：大文件自动分块并行上传
- **进度显示**：实时显示上传进度和速度
- **中断处理**：支持 Ctrl+C 优雅中断

#### 2. 文件下载功能

##### 基本下载
```bash
# 单线程下载
python wss.py download "https://www.wenshushu.cn/f/xxxxxxxx"
python wss.py d "链接"  # 使用别名

# 多线程下载（1-16线程）
python wss.py d "链接" -t 4   # 4线程
python wss.py d "链接" -t 8   # 8线程
```

##### 断点续传
```bash
# 启用断点续传
python wss.py d "链接" -c

# 多线程断点续传
python wss.py d "链接" -t 4 -c
```

##### 下载功能特性
- **多线程下载**：IDM 风格的多连接并行下载
- **智能适配**：自动适配 Range 和非 Range 服务器
- **断点续传**：支持单线程和多线程断点续传
- **连接状态**：实时显示每个线程的下载状态
- **故障转移**：多线程失败时自动回退到单线程
- **文件完整性**：下载完成后验证文件大小

#### 3. 用户管理系统

##### 登录管理
```bash
# 交互式登录管理界面
python wss.py login

# 直接使用 TOKEN 登录
python wss.py login "30Bxxxxxxxxxxxxxxxxxxxxxxxx"

# 退出当前账户
python wss.py unlogin
```

##### 多用户功能
- **自动保存**：登录成功后自动保存用户信息
- **多账户支持**：可保存多个不同用户的 TOKEN
- **快速切换**：登录时可从已保存账户中选择
- **信息展示**：显示用户名、手机号、最后登录时间
- **智能管理**：自动更新登录时间，检测无效 TOKEN

##### TOKEN 获取方法
1. 访问 https://www.wenshushu.cn 并登录
2. 按 F12 打开开发者工具
3. 切换到 Network（网络）标签
4. 刷新页面或进行任意操作
5. 找到请求的 Request Headers
6. 复制 X-TOKEN 字段（通常以 30 或 31 开头）

#### 4. 代理支持

```bash
# HTTP 代理
python wss.py u file.txt -p http://127.0.0.1:8080

# HTTPS 代理
python wss.py d "链接" -p https://proxy.example.com:3128

# SOCKS 代理
python wss.py u file.txt -p socks5://127.0.0.1:1080
```

#### 5. 多语言支持

```bash
# 中文界面（默认）
python wss.py u file.txt

# 英文界面
python wss.py u file.txt -e
python wss.py d "链接" --en
```

### 使用示例集合

#### 日常使用场景
```bash
# 快速上传并生成随机取件码
python wss.py u document.pdf -r

# 大文件多线程高速下载
python wss.py d "链接" -t 8 -c

# 使用代理和账户上传重要文件
python wss.py u important.zip -l -k 2024 -p http://proxy

# 英文界面批量下载
python wss.py d "链接1" -e -t 4 -c
python wss.py d "链接2" -e -t 4 -c
```

## 文件结构说明

```
wenshushu/
├── wss.py                 # 主程序（完整功能版本）
├── pyproject.toml         # 项目配置和依赖管理
├── uv.lock               # uv 锁定文件
├── README.md             # 项目说明文档
├── back/                 # 历史版本和分离功能版本
│   ├── wss_origin.py     # 原始基础版本
│   ├── wss_continue.py   # 断点续传版本
│   ├── wss_dir.py        # 压缩目录上传版本
│   ├── wss_login.py      # 用户登录版本
│   └── wss_multi.py      # 多文件下载版本
├── token.txt             # 当前登录用户 token（自动生成）
├── user_tokens.json      # 多用户 token 存储（自动生成）
```

## 高级功能详解

### 1. 智能下载系统
- **服务器检测**：自动检测服务器是否支持 Range 请求
- **动态分块**：根据文件大小和线程数智能分配下载块
- **连接池管理**：每个线程使用独立的 HTTP 连接
- **断点续传**：支持多线程下载的精确断点续传

### 2. 多用户 TOKEN 管理
- **安全存储**：TOKEN 和用户信息安全存储在本地
- **自动验证**：启动时自动验证 TOKEN 有效性
- **批量管理**：支持管理多个账户，快速切换

### 3. 目录处理系统
- **自动压缩**：目录自动压缩为 tar.gz 格式
- **压缩优化**：显示压缩时间和文件大小
- **临时文件清理**：上传完成后自动清理临时文件

### 4. 中断处理机制
- **优雅中断**：第一次 Ctrl+C 优雅退出并保存状态
- **强制退出**：第二次 Ctrl+C 强制退出
- **状态保存**：断点续传信息自动保存

## 故障排除

### 常见问题解决

1. **TOKEN 无效**
   ```bash
   # 清理无效 token 并重新登录
   python wss.py unlogin
   python wss.py login
   ```

2. **下载失败**
   ```bash
   # 尝试单线程下载
   python wss.py d "链接" -t 1
   
   # 启用断点续传
   python wss.py d "链接" -c
   ```

3. **网络问题**
   ```bash
   # 使用代理
   python wss.py d "链接" -p http://proxy:port
   ```

4. **权限问题**
   ```bash
   # 使用已登录账户
   python wss.py u file.txt -l
   ```

## 版本更新日志

- **v5.0.0** - 多用户支持和命令优化
  - 新增命令别名：`u`(upload), `d`(download)
  - 多用户 token 管理系统
  - 增强的登录管理界面
  - 默认匿名登录，按需用户登录
  - 退出确认机制
- **v4.0.0** - 新参数结构，优化用户体验
- **v3.0.0** - 完整整合版本，包含所有功能
- **v2.0.0** - 分离功能版本
- **v1.0.0** - 基础版本
