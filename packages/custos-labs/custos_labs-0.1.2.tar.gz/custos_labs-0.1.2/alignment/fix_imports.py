import os

def fix_imports(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(subdir, file)
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = content.replace("from custos", "from custos")
                new_content = new_content.replace("import custos", "import custos")

                if content != new_content:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"✅ Fixed imports in: {full_path}")

fix_imports(".")
