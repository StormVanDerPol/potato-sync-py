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

    keys = ["size", "modified"]

    # is this how closures work in python?
    def get_diffs():
        # List where differences are stored.
        diffs = []

        for index, remote_entry in enumerate(remote):

            # Gets matching local entry
            local_entry = next(
                (entry for entry in local if entry["name"] == remote_entry["name"]),
                None,
            )

            diff = {"name": remote_entry["name"]}

            for key in keys:
                if local_entry[key] and remote_entry[key]:

                    largest = "equal"
                    if remote_entry[key] > local_entry[key]:
                        largest = "remote"
                    elif remote_entry[key] < local_entry[key]:
                        largest = "local"

                    diff[key] = {
                        "isdifferent": remote_entry[key] != local_entry[key],
                        "highest": largest,
                    }
                else:
                    diff[key] = {
                        "isdifferent": None,
                        "highest": None,
                    }

            diffs.append(diff)
        return diffs

    diffs = get_diffs()

    if log:
        print(chalk.yellow("\n--- differences ---"))
        print(json.dumps(diffs, indent=4, sort_keys=True))

    def get_action_from_diffs():

        newest_copy = "UNDECIDED"

        for diff in diffs:
            # if timestamp is not different, move on
            if not diff["modified"]["isdifferent"]:
                continue

            if (
                newest_copy != "UNDECIDED"
                and diff["modified"]["highest"] != newest_copy
            ):
                print("Warning: Some files are older, some newer")
                print("likely due to restoring a back-up partially")
                print("please restore the entire backup, and try again.")
                return "ABORT"

            newest_copy = diff["modified"]["highest"]

        # Abort if timestamps all match up
        if newest_copy == "UNDECIDED":
            print("Timestamps are equal, files are likely not modified")
            return "ABORT"

        if newest_copy == "local":
            print("Local has most recent files")
            return "PUSH"
        if newest_copy == "remote":
            print("Remote has most recent files")
            return "PULL"

    action = get_action_from_diffs()
    return action
