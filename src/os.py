import platform

# This function detects the OS the user is running and if Valorant is officially supported in said platform
# returns ["operating system" (string), "Runs Valorant" (bool)]
def get_os():   
    system = platform.system()
    
    if system == "Windows":
        # Detects if Windows version **is not** 10 or 11
        if platform.win32_ver()[0] != str(10 or 11):
            return f"Windows {platform.win32_ver()[0]} {platform.win32_edition()} {platform.win32_ver()[1]}", False
        
        # Workaround for Windows 11 being detected as Windows 10, might not be necessary in the future
        # https://github.com/python/cpython/issues/89545
        if int(platform.win32_ver()[1].split(".")[-1]) >= 22000:
            return f"Windows 11 {platform.win32_edition()} {platform.win32_ver()[1]}", True
        else:
            return f"Windows 10 {platform.win32_edition()} {platform.win32_ver()[1]}", True
        

    # Handles other Operating systems, such as Linux or Mac OS
    else:
        return "Non-Windows operating system", False
