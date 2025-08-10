# RWS Client (Rust WebSocket Client)

一个高性能的 WebSocket 客户端库，使用 Rust 实现核心功能，通过 PyO3 提供 Python 接口。
相较于websocket-client的python开源库，性能提升了500%以上，能够支持大批量的ws推送，不会对CPU造成特别大的负载压力。

## 特性

- 高性能：核心使用 Rust 实现
- 异步支持：完全支持 Python asyncio
- 多连接：支持同时管理多个 WebSocket 连接
- 事件驱动：支持 on_message、on_open、on_close 回调

## 安装

### 前置要求

如果只是作为python包使用rws client的话，那么不需要安装rust环境，直接走从pypi安装逻辑即可

1. Python 3.11 或更高版本
2. Rust 工具链
   ```bash
   # 安装 Rust
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   
   # 重新加载环境变量
   source "$HOME/.cargo/env"
   
   # 验证安装
   cargo --version
   rustc --version
   ```

### 从 PyPI 安装

```bash
pip install rws-client
# 或者使用 poetry
poetry add rws-client
```

### 故障排除

如果遇到 "Cargo metadata failed" 错误，请检查：

1. Rust 是否正确安装：
   ```bash
   cargo --version
   ```

2. 环境变量是否正确设置：
   ```bash
   echo $PATH | grep cargo
   ```

3. 如果没有找到 cargo，手动添加到 PATH：
   ```bash
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

4. 确保系统有必要的编译工具：
   
   Ubuntu/Debian:
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential pkg-config libssl-dev
   ```
   
   CentOS/RHEL:
   ```bash
   sudo yum groupinstall "Development Tools"
   sudo yum install openssl-devel
   ```

## 使用示例

...（其余内容保持不变） 