"""
锐网(RyNet): 一个网络服务器管理工具, 后端程序: Faskapi + Uvicorn + Nginx + ArangoDB + SeaWeedFS

更多内容请前往官网查阅: admin.rymaa.cn
作者: 锐白
主页: rybby.cn, ry.rymaa.cn
邮箱: rybby@163.com
"""


import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

def vdump(var, indent=0):
    if isinstance(var, dict):
        print(' ' * indent + 'array({})'.format(len(var)))
        for key, value in var.items():
            print(' ' * (indent + 2) + f'[{repr(key)}] => ', end='')
            vdump(value, indent + 4)
    elif isinstance(var, list):
        print(' ' * indent + f'array({len(var)})')
        for item in var:
            print(' ' * (indent + 2) + '[{}] => '.format(var.index(item)), end='')
            vdump(item, indent + 4)
    else:
        print(f'{type(var).__name__}({repr(var)})')

def is_linux():
    return sys.platform == "linux" or sys.platform == "linux2"

def is_windows():
    return sys.platform == "win32"

def find_nginx():
    """自动查找 nginx.exe 路径"""
    # 检查环境变量中的路径
    for path in os.environ["PATH"].split(os.pathsep):
        nginx_path = os.path.join(path, "nginx.exe")
        if os.path.isfile(nginx_path):
            return Path(nginx_path).parent
    # 尝试常见安装路径
    for common_path in [
        r"C:\nginx",
        r"C:\Program Files\nginx",
        r"C:\Program Files (x86)\nginx",
        r"D:\www\nginx",
        r"D:\nginx",
        r"D:\Program Files\nginx",
        r"D:\Program Files (x86)\nginx"
    ]:
        nginx_path = os.path.join(common_path, "nginx.exe")
        if os.path.isfile(nginx_path):
            return Path(nginx_path).parent
    raise FileNotFoundError("Not found nginx.exe")

def start_venv():
    try:
        if is_linux():
            cmd = ["source", "rynetenv/bin/activate", "> /dev/null 2>&1 &"]
            cmd = " ".join(cmd)
            subprocess.run(cmd, shell=True, start_new_session=True)
        elif is_windows():
            subprocess.run(["\\rynetenv\\Scripts\\activate"], shell=True, start_new_session=True)
        print("Ok: Virtual environment Start Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Virtual environment Start Fail: {e}")
        return False

def stop_venv():
    try:
        if is_linux():
            subprocess.run(["deactivate"], shell=True)
        elif is_windows():
            subprocess.run(["\\rynetenv\\Scripts\\deactivate"], shell=True)
        print("Ok: Virtual environment Stop Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Virtual environment Stop Fail: {e}")
        return False

def start_nginx():
    try:
        if is_linux():
            cmd = ["sudo", "systemctl", "start", "nginx", "> /dev/null 2>&1 &"]
            cmd = " ".join(cmd)
            subprocess.run(cmd, shell=True, start_new_session=True)
        elif is_windows():
            original_dir = os.getcwd()  # 保存当前目录
            nginx_dir = find_nginx()
            os.chdir(nginx_dir)
            subprocess.run("start /B nginx.exe > NUL 2>&1", shell=True, start_new_session=True)
            os.chdir(original_dir)
        print("Ok: Nginx Start Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Nginx Start Fail: {e}")
        return False

def stop_nginx():
    try:
        if is_linux():
            subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
        elif is_windows():
            subprocess.run(["taskkill", "/F", "/T", "/IM", "nginx.exe"], shell=True)
        print("Ok: Nginx Stop Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Nginx Stop Fail: {e}")
        return False

def create_default_config(conf_path):
    """创建默认的nginx配置文件"""
    os.makedirs(os.path.dirname(conf_path), exist_ok=True)
    default_config = """
worker_processes  1;
events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    server {
        listen       80;
        server_name  localhost;
        location / {
            root   html;
            index  index.html index.htm;
        }
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
"""
    with open(conf_path, "w") as f:
        f.write(default_config)

def start_uvi(host: str = "0.0.0.0", port: int = 8000, background: bool = True):
    try:
        if is_linux() and background:
            # 使用 nohup 和 & 在 Linux 后台运行
            cmd = ["sudo", "nohup", "uvicorn", "api:app", "--host", str(host), "--port", str(port), "> /dev/null 2>&1 &"]
            cmd = " ".join(cmd)
            subprocess.run(cmd, shell=True, start_new_session=True)
        elif is_windows() and background:
            # Windows 使用 start 命令后台运行
            cmd = f'start /B uvicorn api:app --host {host} --port {str(port)} > NUL 2>&1'
            subprocess.run(cmd, shell=True, start_new_session=True)
        else:
            return
        
        print("Ok: Uvicorn Start Success")
        print(f"Uvicorn Started on {host}:{port}" + (" (Background)" if background else ""))
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Uvicorn Start Fail: {e}")
        return False

def stop_uvi():
    try:
        if is_linux():
            subprocess.run(["sudo", "pkill", "-f", "gunicorn"], shell=True)
        elif is_windows():
            subprocess.run(["taskkill", "/f", "/im", "uvicorn.exe"], shell=True)
        else:
            return
        print("Ok: Uvicorn Stop Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: Uvicorn Stop Fail: {e}")
        return False

def start_arangodb() -> bool:
    """启动 ArangoDB 服务"""
    try:
        # Linux/macOS (需根据实际路径调整)
        if is_linux():
            cmd = ["sudo", "systemctl", "start", "arangodb", "> /dev/null 2>&1 &"]
            cmd = " ".join(cmd)
            subprocess.run(cmd, shell=True, start_new_session=True)
        # Windows (需确保 ArangoDB 已安装为服务)
        elif is_windows():
            subprocess.run(["net", "start", "ArangoDB"], shell=True, start_new_session=True)
        print("Ok: ArangoDB Start Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: ArangoDB Start Fail: {e}")
        return False

def stop_arangodb() -> bool:
    """停止 ArangoDB 服务"""
    try:
        # Linux/macOS
        if is_linux():
            subprocess.run(["sudo", "systemctl", "stop", "arangodb"], shell=True)
        # Windows
        elif is_windows():
            subprocess.run(["net", "stop", "ArangoDB"], shell=True)
        print("Ok: ArangoDB Stop Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Err: ArangoDB Stop Fail: {e}")
        return False

def start_service():
    start_venv()
    start_nginx()
    start_uvi()
    start_arangodb()

def stop_service():
    stop_venv()
    stop_nginx()
    stop_uvi()
    stop_arangodb()

def add_host():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def del_host():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def list_host():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def edit_conf():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def python_ver():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def nginx_ver():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def arangodb_ver():
    if is_linux():
        subprocess.run(["sudo", "systemctl", "stop", "nginx"], shell=True)
    elif is_windows():
        subprocess.run(["taskkill", "/F"], shell=True)
        print("Ok: Nginx Stop Success")

def handle_option(option):
    try:
        if option == '1':
            start_venv()
        elif option == '2':
            stop_venv()
        elif option == '3':
            start_nginx()
        elif option == '4':
            stop_nginx()
        elif option == '5':
            start_uvi()
        elif option == '6':
            stop_uvi()
        elif option == '7':
            start_arangodb()
        elif option == '8':
            stop_arangodb()
        elif option == '9':
            start_service()
        elif option == '0':
            stop_service()
        else:
            print("Invalid option")
    except Exception as e:
        print(f"Error: {str(e)}")

def help():
    print("""
+-------------------------------------------+
|    RyNet: Net Server Management Script    |
+-------------------------------------------+
|               admin.rymaa.cn              |
+-------------------------------------------+

Usage:
    python ryhttp.py [option]

Options:
    1    Start virtual environment
    2    Stop virtual environment
    3    Start Nginx
    4    Stop Nginx
    5    Start Uvicorn
    6    Stop Uvicorn
    7    Start ArangoDB
    8    Stop ArangoDB
    9    Start Service
    0    Stop Service
    c    Check Service Status
    q    Quit
    ah   Add Host
    dh   Del Host
    lh   List Host
    ef   Edit Config
    pv   Python Versions
    nv   Nginx Versions
    av   ArangoDB Versions
    -h, --help   Show help
    -v, --version   Show version

Other info:
    add webdir: mkdir www
    add venv: python -m venv venv
    install python pkg: pip install fastapi uvicorn
""")

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, add_help=False)
    parser.add_argument('option', nargs='?')
    parser.add_argument('-v', '--version', help='Show version')
    parser.add_argument('-h', '--help', help='Show help')

    args = parser.parse_args()
    
    if args.help:
        help()
        return

    if args.option:
        handle_option(args.option)
        return
    
    # Interactive menu
    while True:
        print("\nServer Management Menu\n")
        print("  1    Start virtual environment")
        print("  2    Stop virtual environment")
        print("  3    Start Nginx")
        print("  4    Stop Nginx")
        print("  5    Start Uvicorn")
        print("  6    Stop Uvicorn")
        print("  7    Start ArangoDB")
        print("  8    Stop ArangoDB")
        print("  9    Start Service")
        print("  0    Stop Service")
        print("  c    Check Service Status")
        print("  q    Quit")
        print("  ah   Add Host")
        print("  dh   Del Host")
        print("  lh   List Host")
        print("  ef   Edit Config")
        print("  pv   Python Versions")
        print("  nv   Nginx Versions")
        print("  av   ArangoDB Versions")
        
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            handle_option(choice)
        elif choice == 'q':
            break
        elif choice == 'ah':
            add_host()
        elif choice == 'dh':
            del_host()
        elif choice == 'lh':
            list_host()
        elif choice == 'ef':
            edit_conf()
        elif choice == 'pv':
            python_ver()
        elif choice == 'nv':
            nginx_ver()
        elif choice == 'av':
            arangodb_ver()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()