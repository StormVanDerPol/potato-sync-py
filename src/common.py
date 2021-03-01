servername = "potatoserver"


def is_serverfile(file):
    """Checks if file includes server name and wether it's a backup file"""
    if file["name"].endswith(".old") or file["name"].endswith(".bak"):
        return False
    return file["name"].lower().startswith(servername.lower())
