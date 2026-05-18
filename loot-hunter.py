import os
import re
import hashlib
import sys

# Configuration des couleurs ANSI
C_BLUE    = "\033[38;5;39m"
C_GREEN   = "\033[38;5;76m"
C_RED     = "\033[38;5;196m"
C_YELLOW  = "\033[38;5;220m"
C_CYAN    = "\033[38;5;87m"
C_GRAY    = "\033[38;5;244m"
RESET     = "\033[0m"

# Extensions et Noms de fichiers hautement critiques en CTF / Pentest
LOOT_EXTENSIONS = ('.txt', '.conf', '.log', '.key', '.env', '.json', '.bak', '.sql', '.db')
LOOT_FILENAMES  = ('id_rsa', 'id_dsa', 'wp-config.php', 'config.php', '.bash_history', '.zsh_history', 'credentials', 'passwd')

KEYWORDS = [r"pass", r"key", r"admin", r"secret", r"flag", r"token", r"id_rsa", r"db_password"]

def get_hash(path):
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()[:10]
    except:
        return "----------"

def print_header(targets):
    targets_str = ", ".join(targets)
    if len(targets_str) > 39:
        targets_str = targets_str[:36] + "..."
    banner = f"""
{C_CYAN}┌────────────────────────────────────────────────────────┐
│ {C_BLUE}🎯 CTF AUTOMATIC LOOT HUNTER (v1.0){C_CYAN}                     │
│ {C_GRAY}Zones explorées : {targets_str:<37}{C_CYAN} │
└────────────────────────────────────────────────────────┘{RESET}"""
    print(banner)

def scan():
    # Si l'utilisateur fournit un argument (ex: /), on prend ça. 
    # Sinon, le script cible AUTOMATIQUEMENT les dossiers les plus juteux de Linux.
    if len(sys.argv) > 1:
        target_dirs = [os.path.abspath(sys.argv[1])]
    else:
        # Liste de dossiers cibles prioritaires en CTF
        potential_targets = ['/home', '/root', '/var/www', '/tmp', '/dev/shm', '/mnt', '/opt']
        target_dirs = [d for d in potential_targets if os.path.exists(d)]
        
        # Si on est sur une machine Windows ou un environnement custom, on se rabat sur le dossier actuel
        if not target_dirs:
            target_dirs = [os.getcwd()]

    print_header(target_dirs)

    tree_data = {}
    
    # Parcours automatique des dossiers cibles
    for base_dir in target_dirs:
        for root, _, files in os.walk(base_dir):
            # On ignore les répertoires systèmes virtuels ou inutiles pour éviter de freeze
            if any(x in root for x in ['/proc', '/sys', '/dev', '.git', '__pycache__', '/var/lib/docker']):
                continue
                
            valid_files = []
            for f in files:
                f_lower = f.lower()
                # On capture si l'extension est suspecte OU si le nom exact est dans notre liste de loot
                if f_lower.endswith(LOOT_EXTENSIONS) or any(loot_name in f_lower for loot_name in LOOT_FILENAMES):
                    valid_files.append(f)
                    
            if valid_files:
                tree_data[root] = valid_files

    if not tree_data:
        print(f"  {C_RED}❌ Aucun fichier sensible ou suspect détecté dans les zones cibles.{RESET}\n")
        return

    # Affichage des résultats avec le tableau indéformable v3.5
    for folder, files in tree_data.items():
        print(f"\n{C_BLUE}📂 Dossier Sensible : {folder}{RESET}")
        print(f"  {C_CYAN}┌──────┬────────────┬────────────────────────────────────────────────────────┬────────────────────┐{RESET}")
        print(f"  {C_CYAN}│{RESET} ACC  {C_CYAN}│{RESET} SHA256     {C_CYAN}│{RESET} NOM DU FICHIER                                          {C_CYAN}│{RESET} ALERTE / MATCH      {C_CYAN}│{RESET}")
        print(f"  {C_CYAN}├──────┼────────────┼────────────────────────────────────────────────────────┼────────────────────┤{RESET}")

        for f in files:
            full_path = os.path.join(folder, f)
            readable = os.access(full_path, os.R_OK)
            
            status = f"{C_GREEN}[OK]{RESET}" if readable else f"{C_RED}[X ]{RESET}"
            f_hash = get_hash(full_path) if readable else "----------"
            
            alerts = []
            
            # 1. Alerte automatique basée sur le nom du fichier
            if any(loot_name in f.lower() for loot_name in LOOT_FILENAMES):
                alerts.append("CRITICAL_FILE")

            # 2. Alerte basée sur le contenu
            if readable and os.path.getsize(full_path) < 2000000:
                try:
                    with open(full_path, 'r', errors='ignore') as file_content:
                        content = file_content.read()
                        for kw in KEYWORDS:
                            if re.search(kw, content, re.IGNORECASE):
                                alerts.append(kw.upper())
                except:
                    pass
            
            # Formatage strict de l'affichage des alertes
            if alerts:
                # Éliminer les doublons dans les alertes
                alerts = list(set(alerts))
                raw_alert_text = ", ".join(alerts)
                if len(raw_alert_text) > 15:
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

            # Concaténation de la ligne
            line = (
                f"  {C_CYAN}│{RESET} {status} {C_CYAN}│{RESET} {C_GRAY}{f_hash}{RESET} {C_CYAN}│{RESET} "
                f"{display_name}" + " " * space_name + f" {C_CYAN}│{RESET} "
                f"{alert_str}" + " " * space_alert + f"{C_CYAN}│{RESET}"
            )
            print(line)
            
        print(f"  {C_CYAN}└──────┴────────────┴────────────────────────────────────────────────────────┴────────────────────┘{RESET}")

if __name__ == "__main__":
    scan()
