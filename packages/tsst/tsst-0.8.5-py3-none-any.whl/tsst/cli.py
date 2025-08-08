# cli.py
import os
import click

@click.group()
def cli():
    pass

@cli.command()
@click.argument("main_module")  # 大模組，例如 login, trade
@click.argument("sub_module")  # 子模組，例如 order, quote
@click.argument("broker", default="")      # 最小模組，例如 sino, capital
def create_module(main_module: str, sub_module: str, broker: str = None):
    """
    創建新的模組結構。

    範例：
    tsst-cli create-module trade order sino

    Args:
        main_module (str): 大模組名稱
        sub_module (str): 子模組名稱
        broker (str): 最小模組名稱
    """
    if broker is None or broker == "":
        main_module_path = os.path.join("src", "tsst", main_module)
        # 最小模組路徑
        sub_module_path = os.path.join("src", "tsst", main_module, sub_module)

        # 創建券商模組目錄
        os.makedirs(sub_module_path, exist_ok=True)

        # 在主模組中生成檔案
        create_file(os.path.join(main_module_path, "__init__.py"), f"# 初始化大模組 '{sub_module}' 位於大模組 '{main_module}'\n")
        create_file(os.path.join(main_module_path, "base.py"), f"# 大模組 '{sub_module}' 的基礎功能\n")
        create_file(os.path.join(main_module_path, "base_validate.py"), f"# 大模組 '{sub_module}' 的基礎驗證邏輯\n")

        # 在子模組中生成檔案
        create_file(os.path.join(sub_module_path, "__init__.py"), f"# 初始化券商模組 '{sub_module}' 位於大模組 '{main_module}'\n")
        create_file(os.path.join(sub_module_path, "main.py"), f"# 券商模組 '{sub_module}' 的基礎功能\n")
        create_file(os.path.join(sub_module_path, "validate.py"), f"# 券商模組 '{sub_module}' 的基礎驗證邏輯\n")

        click.echo(f"模組結構已創建：{sub_module_path}")
    else:
        # 子模組路徑
        sub_module_path = os.path.join("src", "tsst", main_module, sub_module)
        # 最小模組路徑
        broker_path = os.path.join(sub_module_path, broker)

        # 創建子模組目錄
        os.makedirs(sub_module_path, exist_ok=True)

        # 在子模組中生成檔案
        create_file(os.path.join(sub_module_path, "__init__.py"), f"# 初始化子模組 '{sub_module}' 位於大模組 '{main_module}'\n")
        create_file(os.path.join(sub_module_path, "base.py"), f"# 子模組 '{sub_module}' 的基礎功能\n")
        create_file(os.path.join(sub_module_path, "base_validate.py"), f"# 子模組 '{sub_module}' 的基礎驗證邏輯\n")

        # 創建最小模組目錄
        os.makedirs(broker_path, exist_ok=True)

        # 在最小模組中生成檔案
        create_file(os.path.join(broker_path, "__init__.py"), f"# 初始化券商模組 '{broker}' 位於子模組 '{sub_module}'\n")
        create_file(os.path.join(broker_path, "main.py"), f"# 券商模組 '{broker}' 的主要功能\n")
        create_file(os.path.join(broker_path, "validate.py"), f"# 券商模組 '{broker}' 的驗證邏輯\n")

        click.echo(f"模組結構已創建：{broker_path}")

def create_file(file_path: str, content: str):
    """建立檔案，若存在則不建立。

    Args:
        file_path (str): 檔案路徑
        content (str): 檔案內容
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        click.echo(f"檔案已存在：{file_path}")

if __name__ == "__main__":
    cli()