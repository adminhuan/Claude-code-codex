#!/usr/bin/env python3
"""
AI规则遵守MCP工具命令行接口
提供一键安装和配置功能
"""
import os
import json
import shutil
import subprocess
import sys
from pathlib import Path
import argparse


def get_mcp_config_path():
    """获取Claude Code MCP配置路径"""
    home = Path.home()

    # 常见的Claude Code配置路径
    possible_paths = [
        home / ".claude" / "config.json",
        home / ".config" / "claude" / "config.json",
        home / "Library" / "Application Support" / "Claude" / "config.json",
        home / ".claude-code" / "config.json",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # 如果没找到，返回默认路径
    return home / ".claude" / "config.json"


def install_mcp_server():
    """安装MCP服务器"""
    print("🚀 安装AI规则遵守MCP服务器...")

    # 获取安装路径
    install_dir = Path.home() / ".ai-rule-mcp"
    install_dir.mkdir(exist_ok=True)

    # 复制服务器文件
    package_dir = Path(__file__).parent
    server_file = package_dir / "mcp_server.py"
    config_file = package_dir / "mcp_config.json"

    if server_file.exists():
        shutil.copy2(server_file, install_dir / "mcp_server.py")
        print(f"✅ 服务器已安装到: {install_dir}")
    else:
        # 如果找不到，从当前目录复制
        server_file = Path("mcp_server.py")
        if server_file.exists():
            shutil.copy2(server_file, install_dir / "mcp_server.py")
        else:
            print("❌ 找不到mcp_server.py文件")
            return False

    # 复制整个ai_duet包
    ai_duet_src = package_dir
    ai_duet_dst = install_dir / "ai_duet"

    if ai_duet_src.exists():
        if ai_duet_dst.exists():
            shutil.rmtree(ai_duet_dst)
        shutil.copytree(ai_duet_src, ai_duet_dst)

    print(f"📁 MCP服务器已安装到: {install_dir}")
    return install_dir


def configure_claude_code(install_dir):
    """配置Claude Code MCP"""
    print("⚙️ 配置Claude Code MCP...")

    config_path = get_mcp_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # 读取现有配置
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
    else:
        config = {}

    # 添加MCP服务器配置
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    config["mcpServers"]["ai-rule-mcp"] = {
        "command": "python3",
        "args": ["mcp_server.py"],
        "cwd": str(install_dir),
        "env": {}
    }

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Claude Code配置已更新: {config_path}")
    return True


def uninstall_mcp_server():
    """卸载MCP服务器"""
    print("🗑️ 卸载AI规则遵守MCP服务器...")

    install_dir = Path.home() / ".ai-rule-mcp"
    if install_dir.exists():
        shutil.rmtree(install_dir)
        print("✅ MCP服务器已卸载")

    # 从Claude Code配置中移除
    config_path = get_mcp_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if "mcpServers" in config and "ai-rule-mcp" in config["mcpServers"]:
                del config["mcpServers"]["ai-rule-mcp"]

                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                print("✅ Claude Code配置已清理")
        except:
            pass


def start_server():
    """启动MCP服务器"""
    install_dir = Path.home() / ".ai-rule-mcp"
    server_file = install_dir / "mcp_server.py"

    if not server_file.exists():
        print("❌ MCP服务器未安装，请先运行: ai-rule-mcp install")
        return

    print("🚀 启动MCP服务器...")
    os.chdir(install_dir)
    subprocess.run([sys.executable, "mcp_server.py"])


def main():
    """主命令行接口"""
    parser = argparse.ArgumentParser(description="AI规则遵守MCP工具")
    parser.add_argument("command", choices=["install", "uninstall", "start", "status"],
                       help="命令: install(安装), uninstall(卸载), start(启动), status(状态)")

    args = parser.parse_args()

    if args.command == "install":
        print("🎯 一键安装AI规则遵守MCP工具")
        install_dir = install_mcp_server()
        if install_dir:
            configure_claude_code(install_dir)
            print("\n🎉 安装完成!")
            print("📝 重启Claude Code后即可使用38个AI工具:")
            print("   • 智能规则提醒")
            print("   • 多模式工作流")
            print("   • AI协作功能")
            print("\n💬 试试对Claude Code说: '请提醒我Python编码规范'")

    elif args.command == "uninstall":
        uninstall_mcp_server()
        print("✅ 卸载完成")

    elif args.command == "start":
        start_server()

    elif args.command == "status":
        install_dir = Path.home() / ".ai-rule-mcp"
        if install_dir.exists():
            print("✅ MCP服务器已安装")
            print(f"📁 安装路径: {install_dir}")

            config_path = get_mcp_config_path()
            if config_path.exists():
                print(f"⚙️ 配置文件: {config_path}")
            else:
                print("⚠️ 未找到Claude Code配置文件")
        else:
            print("❌ MCP服务器未安装")


def server():
    """直接启动服务器"""
    start_server()


if __name__ == "__main__":
    main()