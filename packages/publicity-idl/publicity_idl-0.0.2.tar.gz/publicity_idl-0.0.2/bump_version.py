import toml

# 读取pyproject.toml
with open("pyproject.toml", "r", encoding="utf-8") as f:
    config = toml.load(f)

# 获取当前版本号
current_version = config["project"]["version"]
major, minor, patch = map(int, current_version.split("."))

# 递增补丁号（小版本）
new_version = f"{major}.{minor}.{patch + 1}"
config["project"]["version"] = new_version

# 写回pyproject.toml
with open("pyproject.toml", "w", encoding="utf-8") as f:
    toml.dump(config, f)

print(f"版本号已更新：{current_version} → {new_version}")