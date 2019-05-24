import os

if __name__ == '__main__':
    os.system("rm -rf build/ dist/ stfp.spec")
    os.system("pyinstaller --onefile sftp.py")