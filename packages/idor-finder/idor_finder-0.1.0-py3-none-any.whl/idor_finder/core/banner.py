from .utils import colorize, Color


BANNER = r"""
 __ __ _____  _____  ____       ______ _           _           
|  |  |  _  |/  ___|/ __ \      |  ___(_)         | |          
|  |  | | | |\ `--./ /  \/______| |_   _ _ __   __| | ___ _ __ 
|  |  | | | | `--. \ |   ______ |  _| | | '_ \ / _` |/ _ \ '__|
|  |__\ \_/ /\__/ / \__/ /      | |   | | | | | (_| |  __/ |   
 \_____/\___/\____/ \____/       \_|   |_|_| |_|\__,_|\___|_|   
                                                                
"""


def print_banner() -> None:
    print(colorize(BANNER, Color.CYAN))
    print(colorize("IDOR Finder — discovering insecure direct object references.", Color.GREEN))


