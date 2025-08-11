import toml

with open("pyproject.toml", "r") as f:
    data = toml.load(f)

with open("requirements.txt", "r") as f:
    deps = []
    for line in f.readlines():
        line = line.strip()
        deps.append(line)
    data["project"]["dependencies"] = deps

with open("pyproject.toml", "w") as f:
    f.write(toml.dumps(data))