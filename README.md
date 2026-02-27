# NetSentinel
Offline ping dashboard per monitorare switch e dispositivi LAN con stato 🟢/🔴 in tempo reale.


![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

NetSentinel è una piccola app desktop **offline** pensata per monitorare dispositivi di rete (switch/router/server) in LAN tramite **ping (ICMP)**.  
Inserisci gli IP, premi **GO**, e hai subito una vista “da NOC” con stato **🟢 online / 🔴 offline** e orario dell’ultimo controllo.

---

## Cosa fa
- Aggiungi IP manualmente (lista modificabile)
- Avvio/stop del monitoraggio con **GO / STOP**
- Stato chiaro in tabella: **🟢 ATTIVO** / **🔴 NON ATTIVO**
- Timestamp dell’ultimo controllo
- Funziona senza internet: tutto locale

---

## Requisiti
- Windows 10/11 (funziona anche su Linux/macOS)
- Python 3.10+ (consigliato 3.11+)

---

## Avvio rapido (Windows 11)

Apri **PowerShell** nella cartella del progetto e lancia:

```powershell
py --version
py monitor_switches.py

Come si usa

1.Inserisci un IP nel campo IP switch

2.Premi Aggiungi (ripeti per tutti gli IP)

3.Premi GO per iniziare il controllo continuo

4.Premi STOP per fermare il monitoraggio


Output:

dist\monitor_switches.exe


(puoi modificare la lista IP e ripartire)
