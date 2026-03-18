import platform

# This function detects the OS the user is running and if Valorant is officially supported in said platform
# returns ["operating system" (string), "Runs Valorant" (bool)]
def get_os():   
    # Handles Windows operating systems
    if platform.system() == "Windows":
            return f"Windows {platform.win32_ver()[0]} {platform.win32_edition()} {platform.win32_ver()[1]}"
    # Handles other operating systems, such as Linux or Mac OS
    else:
        return "Non-Windows operating system"
