import os
import re
import hashlib
import sys

# Configuration des couleurs ANSI (Compatibilité universelle)
C_BLUE    = "\033[38;5;39m"
C_GREEN   = "\033[38;5;76m"
C_RED     = "\033[38;5;196m"
C_YELLOW  = "\033[38;5;220m"
C_CYAN    = "\033[38;5;87m"
C_GRAY    = "\033[38;5;244m"
RESET     = "\033[0m"

EXTENSIONS = ('.txt', '.csv', '.php', '.pdf', '.conf', '.log', '.key', '.env', '.json')
KEYWORDS = [r"pass", r"key", r"admin", r"secret", r"flag", r"token"]

def get_hash(path):
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()[:10]
    except:
        return "----------"

def print_header(target):
    banner = f"""
{C_CYAN}┌────────────────────────────────────────────────────────┐
│ {C_BLUE}⚡ CTF TREE HUNTER (Standalone Edition v3.5){C_CYAN}           │
│ {C_GRAY}Dossier ciblé : {target:<39}{C_CYAN} │
└────────────────────────────────────────────────────────┘{RESET}"""
    print(banner)

def scan():
    pwd_env = os.environ.get('PWD')
    default_dir = pwd_env if pwd_env else os.getcwd()

    target_dir = sys.argv[1] if len(sys.argv) > 1 else default_dir
    abs_target_dir = os.path.abspath(target_dir)
    
    print_header(abs_target_dir)

    tree_data = {}
    
    for root, _, files in os.walk(abs_target_dir):
        if any(x in root for x in ['/proc', '/sys', '/dev', '.git', '__pycache__']):
            continue
            
        valid_files = [f for f in files if f.lower().endswith(EXTENSIONS)]
        if valid_files:
            tree_data[root] = valid_files

    if not tree_data:
        print(f"  {C_RED}❌ Aucun fichier correspondant aux extensions trouvé dans ce répertoire.{RESET}\n")
        return

    for folder, files in tree_data.items():
        print(f"\n{C_BLUE}📂 Dossier : {folder}{RESET}")
        # Structure de la boîte parfaitement calibrée
        print(f"  {C_CYAN}┌──────┬────────────┬────────────────────────────────────────────────────────┬────────────────────┐{RESET}")
        print(f"  {C_CYAN}│{RESET} ACC  {C_CYAN}│{RESET} SHA256     {C_CYAN}│{RESET} NOM DU FICHIER                                          {C_CYAN}│{RESET} ALERTE / MATCH      {C_CYAN}│{RESET}")
        print(f"  {C_CYAN}├──────┼────────────┼────────────────────────────────────────────────────────┼────────────────────┤{RESET}")

        for f in files:
            full_path = os.path.join(folder, f)
            readable = os.access(full_path, os.R_OK)
            
            status = f"{C_GREEN}[OK]{RESET}" if readable else f"{C_RED}[X ]{RESET}"
            f_hash = get_hash(full_path) if readable else "----------"
            
            alerts = []
            if readable and os.path.getsize(full_path) < 2000000:
                try:
                    with open(full_path, 'r', errors='ignore') as file_content:
                        content = file_content.read()
                        for kw in KEYWORDS:
                            if re.search(kw, content, re.IGNORECASE):
                                alerts.append(kw.upper())
                except:
                    pass
            
            # Formatage de la section Alerte (Tronquage strict si trop long pour éviter les déformations)
            if alerts:
                raw_alert_text = ", ".join(alerts)
                if len(raw_alert_text) > 15: # 15 car [!!] + espace prend déjà 5 caractères
                    raw_alert_text = raw_alert_text[:12] + "..."
                alert_str = f"{C_RED}[!!]{RESET} {raw_alert_text}"
                alert_len = 5 + len(raw_alert_text)
            else:
                alert_str = f"{C_GRAY}Aucun{RESET}"
                alert_len = 5

            # Limitation stricte du nom du fichier
            if len(f) > 54:
                display_name = f[:51] + "..."
            else:
                display_name = f
            
            space_name = 54 - len(display_name)
            space_alert = 20 - alert_len

            # Concaténation de la ligne avec retraits exacts
            line = (
                f"  {C_CYAN}│{RESET} {status} {C_CYAN}│{RESET} {C_GRAY}{f_hash}{RESET} {C_CYAN}│{RESET} "
                f"{display_name}" + " " * space_name + f" {C_CYAN}│{RESET} "
                f"{alert_str}" + " " * space_alert + f"{C_CYAN}│{RESET}"
            )
            print(line)
            
        print(f"  {C_CYAN}└──────┴────────────┴────────────────────────────────────────────────────────┴────────────────────┘{RESET}")

if __name__ == "__main__":
    scan()
