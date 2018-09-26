import os, shutil, subprocess, stat
from git import Repo
from distutils.dir_util import copy_tree

mvBlist = ['.git', 'update.py', 'backups', 'config.py', 'application.yml', 'Lavalink.jar', 'tmp', '__pycache__', 'Pipfile']
pipe = subprocess.Popen("git ls-remote", shell=True, cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
repo = Repo(path=os.getcwd())
(out, error) = pipe.communicate()
out = out.decode("utf-8")
remote = out[:40]
local = str(repo.head.object)

def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
    else:
        try:
            shutil.copyfile(src, dest)
        except PermissionError:
            print("Skipping file.")

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

if remote != local:
    cwd = os.getcwd()
    try:
        os.mkdir(os.path.join(cwd, "backups", local[:6]))
    except FileExistsError:
        print("Folder already exists.")
    for filename in os.listdir(cwd):
        if filename not in mvBlist:
            if os.path.isdir(filename):
                # do directory stuff
                shutil.copytree(os.path.join(cwd, filename), os.path.join(cwd, "backups", local[:6], filename))
                shutil.rmtree(os.path.join(cwd, filename))
            else:
                # do regular file stuff
                shutil.move(os.path.join(cwd, filename), os.path.join(cwd, "backups", local[:6]))
    Repo.clone_from("git://github.com/NiceAesth/Sunny.git", "tmp")
    recursive_overwrite('tmp', cwd)
    shutil.rmtree('tmp', onerror=del_rw)
    exec(compile(open('run.py', "rb").read(), 'run.py', 'exec'))
    