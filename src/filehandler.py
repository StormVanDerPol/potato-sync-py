import cli
from dateutil import parser as dp
import requests
import json
import chalk
import shutil
import pathlib
from os import getenv, path, listdir, pardir
from halo import Halo
from time import time
import re

worldspath = path.abspath(
    path.join(getenv("APPDATA"), pardir, "LocalLow/IronGate/Valheim/worlds")
)

confpath = path.join(worldspath, "potato-config.json")

def is_serverfile(file):
    servername = get_config()["server-name"]

    pattern = r".*?(?=\.)"
    m = re.search(pattern, file["name"])
    noextname = m.group(0) if m else file["name"]
   

    """Checks if file includes server name and wether it's a backup file"""
    if file["name"].endswith(".old") or file["name"].endswith(".bak"):
        return False
    return noextname.lower() == servername.lower()


def get_token():
    return "Bearer " + get_config()["token"]

def test_auth(token):
    url = "https://api.dropboxapi.com/2/check/user"
    headers = {
        "Authorization":  "Bearer " + token,
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers, data=json.dumps({}))
    return r.status_code == 200

def get_config():

    if not path.exists(confpath):
        return

    with open(confpath, "r") as conf:
        return json.loads(conf.read())
      
def set_config(o):

    with open(confpath, "w") as conf:
        parsed = json.dumps(o)
        conf.write(parsed)

def listfolder():
    url = "https://api.dropboxapi.com/2/files/list_folder"
    headers = {
        "Authorization": get_token(),
        "Content-Type": "application/json",
    }
    data = {"path": ""}
    res = requests.post(url, headers=headers, data=json.dumps(data))

    if res.status_code > 399:
        print(
            chalk.red("Error: " + str(res.status_code) + " while trying to list files")
        )
        cli.error_state(True)
        return

    return res.json()


def trim_file_entry(file_entry):

    time = file_entry["server_modified"]
    parsed = dp.parse(time)
    time_in_seconds = parsed.timestamp()

    return {
        "name": file_entry["name"],
        "size": file_entry["size"],
        "modified": time_in_seconds,
    }


def get_remote():
    filelist = listfolder()

    if not filelist:
        return []

    filtered = filter(is_serverfile, filelist["entries"])
    trimmed = []

    for file in filtered:
        trimmed.append(trim_file_entry(file))

    return trimmed


def get_local():

    local_list = []

    for entry in listdir(worldspath):
        filepath = path.join(worldspath, entry)
        if path.isfile(filepath) and is_serverfile({"name": entry}):

            newFileEntry = {
                "name": entry,
                "size": path.getsize(filepath),
                "modified": path.getmtime(filepath),
            }
            local_list.append(newFileEntry)

    return local_list


def create_backup():
    local = get_local()

    pathlib.Path(path.join(worldspath, "bak")).mkdir(exist_ok=True)

    for entry in local:
        backup = entry["name"] + str(time()) + ".bak"
        shutil.copy(
            path.join(worldspath, entry["name"]),
            path.join(worldspath, "bak", backup),
        )


def delete_backups():
    try:
        shutil.rmtree(path.join(worldspath, "bak"))
        print(chalk.green("Deleted backups"))
    except:
        print(chalk.red("Failed to delete backups"))


def push(local):
    url = "https://content.dropboxapi.com/2/files/upload"

    for entry in local:
        headers = {
            "Authorization": get_token(),
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps(
                {
                    "path": "/" + entry["name"],
                    "mode": {".tag": "overwrite"},
                    "strict_conflict": False,
                }
            ),
        }

        try:
            data = open(path.join(worldspath, entry["name"]), "rb").read()
            try:
                spinner = Halo(chalk.blue("uploading " + entry["name"]))
                spinner.start()
                r = requests.post(url, headers=headers, data=data)
                spinner.stop()
                print(chalk.green("Uploaded " + entry["name"]))

            except:
                print(chalk.red("Failed to upload " + entry["name"]))
        except:
            print(chalk.red("Can't read file " + entry["name"]))


def pull(remote):
    url = "https://content.dropboxapi.com/2/files/download"

    for entry in remote:
        headers = {
            "Authorization": get_token(),
            "Dropbox-API-Arg": '{"path":"/' + entry["name"] + '"}',
        }
        res = requests.post(url, headers=headers, stream=True)

        if res.status_code == 200:
            try:
                with open(path.join(worldspath, entry["name"]), "wb") as f, Halo(
                    chalk.blue("Downloading " + entry["name"]), spinner="dots"
                ) as spinner:
                    res.raw.decode_content = True
                    shutil.copyfileobj(res.raw, f)
                    spinner.stop()
                    print(chalk.green("Downloaded " + entry["name"]))
            except:
                print(chalk.red("Failed downloading " + entry["name"]))
