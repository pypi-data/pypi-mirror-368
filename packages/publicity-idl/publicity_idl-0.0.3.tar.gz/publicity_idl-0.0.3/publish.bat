@echo off
:: 1. 清理旧构建产物（CMD兼容命令）
echo 清理旧构建产物...
if exist dist (
    :: 删除dist目录下所有文件和子目录（/s递归，/q静默）
    rmdir /s /q dist
)
:: 重新创建空的dist目录（可选，hatch build会自动创建）
mkdir dist 2>nul

:: 2. 自动递增版本
echo 自动递增版本号...
python bump_version.py

:: 3. 构建包（生成sdist和wheel）
echo 构建新版本...
hatch build

:: 4. 上传到PyPI
echo 上传到PyPI...
twine upload dist/*