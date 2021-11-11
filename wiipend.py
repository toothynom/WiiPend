import os
import sys
import shutil


# Header info lookup
headers = {
    "wbfs" : {
        "ID" : 512,
        "name": 544
    },
    "iso" : {
        "ID" : 0,
        "name": 32
    }
}

def getGameInfo(filePath: str) -> str:
    """Reads the game header and gets the gameID and gameName

    Parameters
    ----------
    filePath : str
        Location of the iso/wbfs/nkit.iso file to be examined

    Returns
    -------
    str
        a string representing the new folder name
    """
    
    fileExt = "wbfs" if filePath.endswith("wbfs") else "iso"

    with open(filePath, "rb") as f:
        iso = f.read(5000)

        header = headers[fileExt]
        hID = header["ID"]
        hName = header["name"]

        gameID = iso[hID:hID + 6].decode("UTF-8")

        hNameEnd = hName
        while iso[hNameEnd] != 0x00:
            hNameEnd += 1

        gameName = iso[hName:hNameEnd].decode("UTF-8")
    
    if gameID.startswith("G"):
        return gameName + " [" + gameID + "]"

    return gameID + "_" + gameName

def processFolder(dirPath: str) -> str:
    """Gets a list of all the iso/wbfs/nkit.iso files in a folder, fetches
    the proposed folder name for the first iso/wbfs and returns it

    Parameters
    ----------
    dirPath : str
        Directory location to be scanned for files

    Returns
    -------
    str
        a string representing the new folder name
    """

    # List of all the iso/wbfs files in a folder
    files = [file for file in os.scandir(dirPath) if os.path.isfile(file.path) and file.name.endswith((".iso", ".wbfs"))]
    
    # If there's no iso/wbfs in the current directory, skip
    if not len(files):
        return

    return getGameInfo(files[0].path)

def startProcessing(dirPath: str) -> None:
    """Reads the contents of a folder, fixes the folder naming and moves
    any standalone iso/wbfs/nkit.iso files into their own folders

    Parameters
    ----------
    dirPath : str
        Location of the main folder where all game files are

    Returns
    -------
    None
    """

    for item in os.scandir(dirPath):

        try:
            if os.path.isdir(item.path):
                print("Processing folder:" + item.path)
                folderName = processFolder(item.path)
                print("Renamig", item.name, "to:", folderName, "\n")
                os.rename(item.path, dirPath + "/" + folderName)

            elif os.path.isfile(item.path) and item.name.endswith((".iso", ".wbfs")):
                print("Processing standalone file:" + item.path)
                folderName = getGameInfo(item.path)
                print("Creating a sub directory:", folderName)
                os.makedirs(folderName)
                print("Moving", item.name, "to:", folderName, "\n")
                shutil.move(item.path, dirPath + "/" + folderName + "/" + item.name)
        except:
            print("ERROR - Error processing file, folder already exists probably i don't know\n")


if __name__ == "__main__":

    # If no arguments passed start processing the current folder
    if len(sys.argv) == 1:
        startProcessing(os.getcwd())
    elif len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]) and os.path.isdir(sys.argv[1]): startProcessing(sys.argv[1])
        else:
            print("Could not ressolve path:\n  1. Path is not a directory\n  2. Path does not exist")
    elif len(sys.argv) == 3:
        pass
    else:
        print("Usage: python3 wiipend.py <option> <path>")