import json
import chalk


def determine(remote, local, log):

    if log:
        print(chalk.yellow("\n--- remote ---"))
        print(json.dumps(remote, indent=4, sort_keys=True))

        print(chalk.yellow("\n--- local ---"))
        print(json.dumps(local, indent=4, sort_keys=True))

    # Case no files are found, abort
    if len(local) == 0 and len(remote) == 0:
        print("No world files found")
        return "ABORT"

    # Case local copy is absent, pull
    if len(local) == 0:
        print("No local copy found!")
        return "PULL"

    # Case no remote, push
    if len(remote) == 0:
        print("No remote copy found!")
        return "PUSH"

    # Forces PULL if a file is missing locally
    if len(remote) > len(local):
        print("File missing locally")
        return "PULL"

    remote_epoch = list(filter(lambda entry: entry["name"].endswith(".db"), remote))[0]["modified"]
    local_epoch = list(filter(lambda entry: entry["name"].endswith(".db"), local))[0]["modified"]

    if local_epoch > remote_epoch:
        return "PUSH"
    elif  local_epoch < remote_epoch:
        return "PULL"
    elif  local_epoch == remote_epoch:
        print("Timestamps are equal, somehow")
        return "ABORT"
