#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始构建和发布流程${NC}"

# 检查版本号参数
if [ -z "$1" ]; then
    echo "请提供版本号，例如: ./scripts/build_and_publish.sh 0.1.0"
    exit 1
fi

VERSION=$1

# 更新版本号
echo -e "${GREEN}更新版本号到 ${VERSION}${NC}"
sed -i "s/version = \".*\"/version = \"${VERSION}\"/" pyproject.toml

# 清理旧的构建文件
echo -e "${GREEN}清理旧的构建文件${NC}"
rm -rf dist/
rm -rf target/wheels/

# 构建不同平台的 wheel
echo -e "${GREEN}开始构建 wheel${NC}"

# Linux 构建
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
   maturin build --release --strip
fi

# macOS 构建
if [[ "$OSTYPE" == "darwin"* ]]; then
    maturin build --release --strip --universal2
fi

# Windows 构建
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    maturin build --release --strip
fi

# 创建源码分发包
echo -e "${GREEN}创建源码分发包${NC}"
maturin sdist

echo -e "${GREEN}构建完成！${NC}"
echo "发布到 PyPI："
mkdir -p dist/
cp target/wheels/* dist/