import requests
from datetime import datetime
import os
import hashlib
import json
from datetime import datetime
def scan_dirs(dirname): 
    uploaddir=[]
    uploadfile=[]
    with os.scandir(dirname) as dirs:
        for file in dirs:
            if file.is_file():
                if file.name.endswith(".py") or file.name.endswith(".pt") or file.name.endswith(".pth")or file.name.endswith(".pyc"):
                    uploadfile.append(file.name)
            else:
                uploaddir.append(file.name)
    return uploaddir,uploadfile

def login(passwd,weburl):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d--%H%M")
    acesstoken=timestamp+passwd
    url=weburl+":8888/login/"
    try:
        response=requests.post(url,data={"token":hashlib.sha256(acesstoken.encode('utf-8')).hexdigest()}).json()
    except:
        raise ValueError("passwd or url is wrong")
    if response["allow"]:
        return True
    else:
        raise ValueError("passwd is wrong")
    
def file_hash(path, algo='sha256', bufsize=1<<20):
    h = hashlib.new(algo)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(bufsize), b''):
            h.update(chunk)
    return h.hexdigest()

def uploadfile(url,file,currentdir):
    url=url+":8888/uploadfile/"
    with open(file, 'rb') as f:
        files = {'file': (os.path.basename(file), f)}
        response = requests.post(url,files=files,data={"currentdir":currentdir}).json()
    return response
def checkversion(weburl, acesstoken,basedirs,timestamp):
    url = f"{weburl}:8888/checkversion/"
    response = requests.post(url,data={"timestamp":timestamp,"basedir":basedirs}).json()
    return response.get("version")
#def uploaddirs(currentdir,dirs,acesstoken):
def upload_all_dirs(root, dirs0, weburl, acesstoken,basedir):
    for dir_name in dirs0:
        currentdir = os.path.join(root, dir_name)
        dirs, files = scan_dirs(currentdir)
        uploadcurrentdir=os.path.join(basedir, dir_name)
        # 上传目录信息
        
        url = f"{weburl}:8888/dirs/"
        response = requests.post(url, data={"token": hashlib.sha256(acesstoken.encode('utf-8')).hexdigest(), "dirs": str(dirs),"currentdir":uploadcurrentdir.replace("\\", "/")}).json()
        if not response.get("sucess", False):
            raise RuntimeError("upload timeout")

        # hash 检查
        hashfiledict = {file: file_hash(os.path.join(currentdir, file)) for file in files}
        response = requests.post(f"{weburl}:8888/hashcheck/", data={"data":json.dumps(hashfiledict),"currentdir":uploadcurrentdir.replace("\\", "/"),"token":hashlib.sha256(acesstoken.encode('utf-8')).hexdigest()}).json()

        # 上传文件
        for r in response.get("namelist", []):
            uploadfile(weburl, os.path.join(currentdir, r),uploadcurrentdir.replace("\\", "/"))

        # 递归处理子目录
        if dirs:
            upload_all_dirs(currentdir, dirs, weburl, acesstoken,uploadcurrentdir.replace("\\", "/"))


class AutoBackUp:
    def __init__(self, passwd, weburl, verbose=True):
        token = login(passwd, weburl)
        if not token:
            raise RuntimeError("login failed")

        if verbose:
            print("sucessful login!")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d--%H%M")
        acesstoken = timestamp + passwd

        basedir = os.path.basename(os.getcwd())
        basedirtimestamp=os.path.getatime(os.getcwd())
        version = str(checkversion(weburl,acesstoken,basedir,basedirtimestamp))
        url = f"{weburl}:8888/basedir/"
        response = requests.post(url, data={"token": hashlib.sha256(acesstoken.encode('utf-8')).hexdigest(), "dirs": basedir+version}).json()
        if not response.get("sucess", False):
            raise RuntimeError("wrong passwd!")
 
        # 上传当前目录
        dirs1, files = scan_dirs("./")
        
        url = f"{weburl}:8888/dirs/"
        response = requests.post(url, data={"token":hashlib.sha256(acesstoken.encode('utf-8')).hexdigest(), "dirs": str(dirs1),"currentdir":basedir+version}).json()
        if not response.get("sucess", False):
            raise RuntimeError("upload timeout")

        # hash 检查
        hashfiledict = {file: file_hash(os.path.join("./", file)) for file in files}
        response = requests.post(f"{weburl}:8888/hashcheck/", data={"data":json.dumps(hashfiledict),"currentdir":basedir+version,"token":hashlib.sha256(acesstoken.encode('utf-8')).hexdigest()}).json()
        # 上传文件
        for r in response.get("namelist", []):
            uploadfile(weburl, os.path.join("./", r),currentdir=basedir+version)

        # 递归子目录
        if dirs1:
            upload_all_dirs("./", dirs1, weburl, acesstoken,basedir+version)
        if verbose:
            print("already update!")
