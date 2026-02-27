# NetSentinel

Offline ping dashboard per monitorare switch e dispositivi LAN con stato 🟢/🔴 in tempo reale.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/github/license/viperhack89/NetSentinel)

![NetSentinel Banner](NetSentinel.png)


NetSentinel è una piccola app desktop **offline** pensata per monitorare dispositivi di rete (switch/router/server) in LAN tramite **ping (ICMP)**.  
Inserisci gli IP, premi **GO**, e ottieni una vista “da NOC” con stato **🟢 online / 🔴 offline** e orario dell’ultimo controllo.

---

## Funzioni
- Lista IP modificabile (aggiungi / rimuovi / svuota)
- Avvio e stop del monitoraggio con **GO / STOP**
- Stato in tabella: 🟢 **ATTIVO** / 🔴 **NON ATTIVO**
- Timestamp dell’ultimo controllo
- Nessuna dipendenza da servizi esterni: funziona **offline**

---

## Requisiti
- Windows 10/11 (funziona anche su Linux/macOS)
- Python 3.10+ (consigliato 3.11+)

---

## Avvio rapido (Windows 11)

Apri **PowerShell** nella cartella del progetto:

```powershell
py --version
py monitor_switches.py

Come si usa

1.Inserisci un IP nel campo IP switch

2.Premi Aggiungi (ripeti per tutti gli IP)

3.Premi GO per iniziare il controllo continuo

4.Premi STOP per fermare il monitoraggio (puoi modificare la lista e ripartire)
