# bpcode/cli.py
import os
import sys
import subprocess

def main():
    project_dir = os.path.join(os.path.dirname(__file__), 'bpserver')
    manage_py = os.path.join(project_dir, 'manage.py')

    # 启动 manage.py runserver，后台运行，不占终端
    subprocess.Popen(
        [sys.executable, manage_py, 'runserver', '0.0.0.0:8888'],
        cwd=project_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp
    )
    print("!运行前一定配置环境变量!bpserver 已在后台运行，访问 http://127.0.0.1:8888访问控制面板,访问 http://127.0.0.1:8888/doc查看帮助文档")

if __name__ == "__main__":
    main()
