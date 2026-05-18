import os
import re
import hashlib
import sys
import signal

# Configuration des couleurs ANSI
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

def security_interrupt_handler(sig, frame):
    print(f"\n\n  {C_RED}[!!!] ARRÊT D'URGENCE INTERACTIF : (Ctrl+C) détecté.{RESET}")
    print(f"  {C_YELLOW}[*] Kill-switch activé. Retour au terminal actif.{RESET}\n")
    sys.exit(0)

def print_header(targets):
    targets_str = ", ".join(targets)
    if len(targets_str) > 39:
        targets_str = targets_str[:36] + "..."
    banner = f"""
{C_CYAN}┌────────────────────────────────────────────────────────┐
│ {C_BLUE}🎯 CTF LOOT HUNTER (v1.3 Smart Target)      {C_CYAN}         │
│ {C_GRAY}Zones explorées : {targets_str:<37}{C_CYAN} │
└────────────────────────────────────────────────────────┘{RESET}"""
    print(banner)

def scan():
    signal.signal(signal.SIGINT, security_interrupt_handler)

    # DÉTECTION AUTOMATIQUE SMART
    # Si l'utilisateur donne un argument (ex: /home/emerick), on prend ça.
    if len(sys.argv) > 1:
        target_dirs = [os.path.abspath(sys.argv[1])]
    else:
        # Sinon, s'il fait juste "python3 F-H.py", on scanne automatiquement les dossiers intéressants existants
        potential_targets = ['/home', '/root', '/var/www', '/tmp', '/opt']
        target_dirs = [d for d in potential_targets if os.path.exists(d)]
        
        # Secours si on est dans un environnement restreint ou non-standard
        if not target_dirs:
            pwd_env = os.environ.get('PWD')
            target_dirs = [pwd_env if pwd_env else os.getcwd()]
    
    print_header(target_dirs)

    try:
        # On boucle à travers toutes les cibles définies (une ou plusieurs)
        for base_dir in target_dirs:
            for root, _, files in os.walk(base_dir):
                if any(x in root for x in ['/proc', '/sys', '/dev', '.git', '__pycache__', '/var/lib/docker']):
                    continue
                    
                valid_files = [f for f in files if f.lower().endswith(EXTENSIONS)]
                
                if valid_files:
                    # Correction du bug d'affichage de la v3.7 (root est utilisé proprement)
                    print(f"\n{C_BLUE}📂 Dossier détecté : {root}{RESET}")
                    print(f"  {C_CYAN}┌──────┬────────────┬────────────────────────────────────────────────────────┬────────────────────┐{RESET}")
                    print(f"  {C_CYAN}│{RESET} ACC  {C_CYAN}│{RESET} SHA256     {C_CYAN}│{RESET} NOM DU FICHIER                                          {C_CYAN}│{RESET} ALERTE / MATCH      {C_CYAN}│{RESET}")
                    print(f"  {C_CYAN}├──────┼────────────┼────────────────────────────────────────────────────────┼────────────────────┤{RESET}")

                    for f in valid_files:
                        full_path = os.path.join(root, f)
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
                        
                        if alerts:
                            raw_alert_text = ", ".join(alerts)
                            if len(raw_alert_text) > 15:
                                raw_alert_text = raw_alert_text[:12] + "..."
                            alert_str = f"{C_RED}[!!]{RESET} {raw_alert_text}"
                            alert_len = 5 + len(raw_alert_text)
                        else:
                            alert_str = f"{C_GRAY}Aucun{RESET}"
                            alert_len = 5

                        if len(f) > 54:
                            display_name = f[:51] + "..."
                        else:
                            display_name = f
                        
                        space_name = 54 - len(display_name)
                        space_alert = 20 - alert_len

                        line = (
                            f"  {C_CYAN}│{RESET} {status} {C_CYAN}│{RESET} {C_GRAY}{f_hash}{RESET} {C_CYAN}│{RESET} "
                            f"{display_name}" + " " * space_name + f" {C_CYAN}│{RESET} "
                            f"{alert_str}" + " " * space_alert + f"{C_CYAN}│{RESET}"
                        )
                        print(line)
                        
                    print(f"  {C_CYAN}└──────┴────────────┴────────────────────────────────────────────────────────┴────────────────────┘{RESET}")
                    
    except KeyboardInterrupt:
        security_interrupt_handler(None, None)

if __name__ == "__main__":
    scan()
