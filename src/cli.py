import inquirer
import chalk
import time

import filehandler
from action import determine
from clearscreen import clearscreen

# states:
# default - Displays menu.
# welcome - Displays welcome screen, otherwise equal to default

# get/set for global error state
def error_state(value):
    global err
    if value is None:
        return err
    err = value


def menu(state):

    if state == "welcome":
        clearscreen()
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
    questions = [
        inquirer.List(
            "action",
            message="Choose an action",
            choices=[
                "sync",
                "check",
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

    if selected == "delete cli bak":
        filehandler.delete_backups()
        menu("default")

    if selected == "check":
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
    if selected == "sync":
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
