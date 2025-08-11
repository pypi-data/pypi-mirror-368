#!/usr/bin/env python
# coding: utf-8
import os
import shutil
import sys
import subprocess
def install_linux_packages():
    # 检查是否为Linux系统
    if not sys.platform.startswith('linux'):
        print("当前操作系统不是Linux，跳过安装。")
        return
    

    
    # 要安装的apt软件包列表
    apt_packages_groups = [
        ["python3-pip", "python3-tk", "python3-pandas", "python3-xlsxwriter", "pillow",'python3-statsmodels'],
        ["requests"],
        ["python3-seaborn"],
        ["python3-requests"],
        ["python3-statsmodels"],
        ["python3-numpy"],
        ["python3-scipy"],
        ["python3-matplotlib"],
        ["python3-pyqt5"],
    ]
    print('需要通过sudo apt-get install 安装的是：',apt_packages_groups)
    print('安装示例sudo apt-get install python3-pip')
    # 要安装的pip软件包列表
    pip_packages = ["xlrd", "xlwt", "openpyxl", "sqlalchemy",'python-docx','pycryptodome','packaging','pycryptodome','easypymanager']
    print('需要通过pip3 install 安装的是：',apt_packages_groups)
    print('安装示例pip3 install xlrd')
    print('安装后建议升级pandas：pip3 install pandas --upgrade')

    a=input("\n检测到Linux系统，是否安装依赖包？y/n")
    if a=='N' or a=='n':
        return
    
    success_apt = []
    failed_apt = []
    success_pip = []
    failed_pip = []
    
    # 配置pip镜像源
    try:
        subprocess.run([python_executable, "-m", "pip", "config", "set", "global.index-url", 
                       "https://mirrors.aliyun.com/pypi/simple/"], check=True)
        print("已成功配置pip阿里云镜像源")
    except subprocess.CalledProcessError as e:
        print(f"配置pip镜像源失败: {e}")
    
    # 安装apt软件包
    for group in apt_packages_groups:
        for package in group:
            try:
                print(f"正在通过apt安装 {package}...")
                subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True)
                success_apt.append(package)
                print(f"{package} 安装成功")
            except subprocess.CalledProcessError as e:
                failed_apt.append(package)
                print(f"{package} 安装失败: {e}")
    
    # 安装pip软件包
    for package in pip_packages:
        try:
            print(f"正在通过pip安装 {package}...")
            subprocess.run([python_executable, "-m", "pip",  "install", "--user", package], check=True)
            success_pip.append(package)
            print(f"{package} 安装成功")
        except subprocess.CalledProcessError as e:
            failed_pip.append(package)
            print(f"{package} 安装失败: {e}")
    
    # 打印安装结果
    print("\n安装结果:")
    print(f"通过apt成功安装的包: {', '.join(success_apt)}")
    print(f"通过apt安装失败的包: {', '.join(failed_apt)}")
    print(f"通过pip成功安装的包: {', '.join(success_pip)}")
    print(f"通过pip安装失败的包: {', '.join(failed_pip)}")
 
def update_software(package_name):
    print("正在检查更新...")
    print(f"Python 解释器路径: {python_executable}")
    
    try:
        # 更新包
        if not sys.platform.startswith('linux'):
            subprocess.run(
                [python_executable, "-m", "pip", "install", package_name, "--upgrade"],
                check=True,
                timeout=8,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            subprocess.run(
                [python_executable, "-m", "pip", "install", package_name, "--upgrade","--no-deps"],
                check=True,
                timeout=8,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            	
    except subprocess.TimeoutExpired:
        print("更新超时，请检查网络连接或稍后再试。")
    except subprocess.CalledProcessError as e:
        print(f"更新失败，错误代码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    else:
        print("\n更新操作完成，您可以开展工作。")
        # 运行文件（这里保留了 file_path，但原代码中未定义，需要确保已定义）
    if 1==1:    
        try:
            subprocess.run([python_executable, file_path])
        except NameError:
            print("错误: file_path 未定义")
        except subprocess.TimeoutExpired:
            print("运行文件超时")
        except Exception as e:
            print(f"运行文件时出错: {e}")
            
package_name = "easypv"
package_names = package_name + ".py"
python_executable = shutil.which('python3') or shutil.which('python')



# 获取当前脚本的绝对路径
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, package_names)
# 更新软件
# 获取当前脚本的绝对路径
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, package_names)
setting_file = os.path.join(current_directory, 'setting.cfg')
if sys.platform.startswith('linux') and not os.path.exists(setting_file):
    install_linux_packages()
elif sys.platform.startswith('linux'):
    print("\n检测到Linux系统，但setting.cfg文件已存在，跳过依赖包安装。")

update_software(package_name)

