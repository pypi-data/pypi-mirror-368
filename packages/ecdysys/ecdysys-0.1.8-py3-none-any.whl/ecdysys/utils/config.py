import tomllib as toml
import os

# Opens config file
try:
    cfg_path = os.path.expanduser("~") + "/.config/ecdysys/config.toml"
    with open(cfg_path, "rb") as c:
        cfg = toml.load(c)
except FileNotFoundError:
    print_err(f"No config.toml found at {cfg_path}")
    exit()

# get values from config file
#- Packages managers
try: Pkgms = cfg['pkg_managers']
except KeyError: print_err("No package managers found in config.toml in `pkg_manager`"); exit()
# - Aur helpers
try: Slc_aur =  cfg['aur_helper']
except KeyError: Slc_aur =  str()
#- Post-install scripts
try: Post_install_script = cfg['post_install_script']
except KeyError: Post_install_script = str()
#- Sudo bin
try: Sudobin = cfg['sudobin'] if "/" in cfg['sudobin'] else shutil.which(cfg['sudobin'])
except KeyError: Sudobin = shutil.which("sudo")
#- Insert aur helper in list if pacman and aur helper are set
if "pacman" in Pkgms and Slc_aur: Pkgms.insert(Pkgms.index("pacman") + 1, Slc_aur)

