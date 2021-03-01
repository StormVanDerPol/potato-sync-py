import inquirer
import chalk
import time

import signal
import sys

import filehandler
from action import determine
from clearscreen import clearscreen

from pyfiglet import Figlet

def sigint_handler(sig, frame):
    clearscreen()
    print("Shutting down...")
    sys.exit(0)
    
signal.signal(signal.SIGINT, sigint_handler)

# states:
# default - Displays menu.
# welcome - Displays welcome screen, otherwise equal to default

# get/set for global error state
def error_state(value):
    global err
    if value is None:
        return err
    err = value

def config():
    print(chalk.blue("Needs world name and dropbox token to make this work, make sure dropbox has appropriate rights\n"))

    server_name = input( "[" + chalk.yellow("?") + "] World name (not case sensitive): ")
    token = input( "[" + chalk.yellow("?") + "] Dropbox access token: ")

    is_valid = filehandler.test_auth(token)

    if is_valid:
        filehandler.set_config({"server-name": server_name, "token": token})
        menu("default")
    else:
        clearscreen()
        print(chalk.red("Couldn't communicate with dropbox, try again"))
        config()
        
        


def menu(state):

    if state == "welcome":
        clearscreen()
        f = Figlet(font='slant')
        print(chalk.yellow(f.renderText("Potato Sync 9000")))

        print(
            "Ahoy! Welcome to the hopefully new and improved "
            + chalk.yellow("Potato Sync 9000!")
            + ". Python edition"
        )

        print("Use the " + chalk.blue("sync") + " option to get started\n")
        print(
            chalk.red(
                "Warning!\n\nnever interrupt the CLI as that might cause data corruption\n(Especially when downloading)"
            )
        )
        print(
            chalk.red("in case of data corruption, restore Valheim's or the cli's ")
            + chalk.magenta(".old")
            + chalk.red(" or ")
            + chalk.magenta(".bak")
            + chalk.red(" backups\n")
        )

    print("\n---------------------------")
    conf = filehandler.get_config()

    if not conf:
        config()
        return

    valid_token = filehandler.test_auth(conf["token"])

    if not valid_token:
        print(chalk.red("Couldn't communicate with dropbox!"))

    if not valid_token:
        config()
        return

    print(chalk.green("server name is ") + chalk.blue(conf["server-name"]))
    print(chalk.green("dropbox token is set\n"))

    questions = [
        inquirer.List(
            "action",
            message="Choose an action",
            choices=[
                "sync",
                "check",
                "change settings",
                "delete cli bak",
                "exit",
            ],
        ),
    ]

    selected = inquirer.prompt(questions)["action"]
    clearscreen()
    error_state(False)

    if selected == "exit":
        print(chalk.red("Bye~"))
        time.sleep(1)
    elif selected == "change settings":
        signal.signal(signal.SIGINT, sigint_cancel_edit_config_handler)
        config()
    elif selected == "delete cli bak":
        filehandler.delete_backups()
        menu("default")
    elif selected == "check":
        remote = filehandler.get_remote()
        local = filehandler.get_local()

        if not error_state(None):
            action = determine(remote, local, True).lower()
            print(
                chalk.yellow("\nNext time when using ")
                + chalk.blue("sync")
                + chalk.yellow(", the CLI will ")
                + chalk.blue(action)
            )
        menu("default")
    elif selected == "sync":
        remote = filehandler.get_remote()
        local = filehandler.get_local()
        if not error_state(None):

            filehandler.create_backup()

            action = determine(remote, local, False).lower()
            print(chalk.yellow("\nCLI will ") + chalk.blue(action))
            if action == "push":
                filehandler.push(local)
            elif action == "pull":
                filehandler.pull(remote)
            elif action == "abort":
                print("Aborting...")
        menu("default")
