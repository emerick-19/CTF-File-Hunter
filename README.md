# CTF-File-Hunter and Loot-Hunter

<img width="1774" height="887" alt="FILE HUNTER" src="https://github.com/user-attachments/assets/e5ce4d0a-3abf-412b-93fa-8346087a91e2" />








































------------------------------

#Outil d'énumération récursive et d'exfiltration pour Pentest et CTF
# 🎯 CTF & Pentest Suite : File & Loot Hunter

Une suite d'outils légers en Python, **zéro dépendance**, conçue pour l'énumération récursive rapide, la détection de fichiers sensibles et l'exfiltration de données lors de CTFs ou de missions de Pentest.

---

## 📊 Comparatif des Outils

| Outil | Usage Principal | Comportement | Kill-Switch (`Ctrl+C`) |
| :--- | :--- | :--- | :--- |
| **`loot-hunter.py`** | Pentest / Post-Exploit | Scan global et exfiltration lourde en tâche de fond. | ❌ Non interruptible (conçu pour tourner jusqu'au bout) |

| **`CTF-File-Hunterv1.py`** | CTF (Automatique) | Scan automatique des dossiers clés (`/home`, `/root`...) avec affichage en direct. |  **Oui** (Arrêt instantané) |

| **`File-Hunter.py`** | CTF / Pentest (Ciblé) | Scan précis d'un répertoire spécifique passé en argument. |  **Oui** (Arrêt instantané) |

---

## 🚀 Utilisation (Usage)

### 1. Mode Automatique (Sans spécifier de chemin)
Ces outils ciblent automatiquement les dossiers stratégiques du système informatique (`/home`, `/root`, `/tmp`, etc.) ou le répertoire courant.

```bash
# Pour de l'exfiltration lourde en mode Pentest
python3 loot-hunter.py

# Pour une recherche rapide et interactive en CTF (v1.3 Smart Target)
python3 CTF-File-Hunterv1.py

loot-hunter is use for real exfiltration. It can be use on a CTF but you cant interrupt it. That's the reason why is more for Pentesting. I creat CTF-File-Hunterv1 for CTF exfiltration

usage:

#he will automatically check in all directories. You don't need to precise the directory

python3 loot-hunter.py

python CTF-File-Hunterv1.py

usage:
#Here you need to precise the path 

python3 File-hunter.py path

Ex: File-Hunter.py /home/ubuntu
