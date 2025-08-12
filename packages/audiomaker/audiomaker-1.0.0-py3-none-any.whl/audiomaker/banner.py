def print_banner():
  banner = r"""
     _         _ _        __  __       _             
    / \  _   _| (_) __ _ |  \/  | __ _| | _____ _ __ 
   / _ \| | | | | |/ _` || |\/| |/ _` | |/ / _ \ '__|
  / ___ \ |_| | | | (_| || |  | | (_| |   <  __/ |   
 /_/   \_\__,_|_|_|\__, ||_|  |_|\__,_|_|\_\___|_|   
                    |___/                            
  """
  tagline = "Unlimited text, one seamless voice."
  print("\033[36m" + banner + "\033[0m")  # Cyan text
  print("\033[33m" + tagline + "\033[0m\n")  # Yellow text
