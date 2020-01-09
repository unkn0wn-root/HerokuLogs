###
import sys
import os.path
import platform
import subprocess
import argparse
from shutil import which


class AppNotFound(Exception):
    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload

    def __str__(self):
        return str(self.message)


def exist_tool(name):
    if which(name) is None:
        raise AppNotFound(f"Can't find {format(name)} or not installed. Aborting...")


try:
    exist_tool('heroku')
except AppNotFound as err:
    print(str(err))
    sys.exit(1)


def test_crdentials():
    h_cred = subprocess.run(['heroku', 'auth:token'], stdout=subprocess.PIPE)
    return h_cred


if test_crdentials() is None:
    print("Can't find any credentials. Running heroku login...")

    def run_heroku_login():
        h_login = subprocess.Popen(['heroku login'], stdout=subprocess.PIPE)
        h_login.wait()
        return h_login

    try:
        h_login_res = run_heroku_login()
        print("Login Successfully!")
        print(h_login_res)
    except Exception as ex:
        print(ex.message)
        sys.exit(1)


def execute(*commands):
    if platform.system() == "Windows":
        new_window_command = "cmd.exe /c start".split()
    else:  # XXX this can be made more portable
        new_window_command = "gnome-terminal --disable-factory -e".split()

    # Start two terminal parallel and run commands defined in execute function
    processes = [subprocess.Popen(new_window_command + ['heroku logs ' + command],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
                 for command in commands]

    # Wait for new output until finished
    for process in processes:
        errors = process.wait()
        if process.returncode != 0:
            print(process.returncode, errors)

        if process.returncode == 0:
            print(f" Process {process.pid} finished with exit code {process.returncode}")


parser = argparse.ArgumentParser(description='Heroku logs multiple processes')
parser.add_argument("-p", type=str, dest='path', help="Define path to heroku commands")
args = parser.parse_args()

if args.path:
    if os.path.isfile(args.path):
        try:
            with open(args.path) as heroku_cmd:
                list_cmd = []
                for line in heroku_cmd:
                    list_cmd.append(line)
            execute(*list_cmd)
        except IOError as err:
            raise
    else:
        print(f"Can't find file in {args.path}. Check if file exist!")
else:
    execute("-t --app=MyApp --num=1000")
