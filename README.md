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



Aggiornamento

# NetSentinel

![NetSentinel Logo](netsentinel_logo.png)

**NetSentinel** è un piccolo progetto desktop nato con un obiettivo molto semplice: avere sotto controllo switch e dispositivi di rete in LAN in modo rapido, visivo e senza dipendere da servizi esterni.

Con l’ultima versione il progetto è cresciuto parecchio: non è più solo uno script Python con una lista di IP, ma una vera applicazione desktop con **nuovo layout grafico**, **mappa di rete**, **branding dedicato** e anche una **versione eseguibile `.exe` per Windows**.

L’idea alla base resta la stessa: creare uno strumento pratico, leggero e immediato, pensato per chi lavora ogni giorno in ambito IT e ha bisogno di vedere in pochi secondi cosa è online, cosa è offline e come sono distribuiti gli apparati.

---

## Cosa fa NetSentinel

NetSentinel permette di monitorare dispositivi di rete in ambiente locale e di gestirli in modo più ordinato rispetto a una semplice lista di IP.

Con l’app puoi:

- visualizzare lo stato dei dispositivi in tempo reale
- gestire una lista di switch e apparati di rete
- vedere l’ultimo controllo effettuato
- costruire una mappa visuale della rete
- spostare i nodi liberamente
- creare collegamenti tra apparati
- aprire una finestra di dettaglio per operazioni rapide via SSH
- salvare e ricaricare la configurazione locale

---

## Le novità di questa versione

Questa release introduce diversi cambiamenti importanti rispetto alla versione iniziale.

### Nuovo layout grafico
L’interfaccia è stata completamente rivista con uno stile più moderno, pulito e leggibile.  
L’obiettivo era rendere l’app più piacevole da usare ma soprattutto più chiara dal punto di vista operativo.

Tra le principali modifiche:

- header con logo NetSentinel
- pulsanti **GO** e **STOP** più evidenti
- organizzazione migliore della schermata
- separazione tra **Lista Switch** e **Mappa di Rete**
- interfaccia più coerente e più ordinata

### Versione `.exe` per Windows
Il progetto ora può essere distribuito anche come **eseguibile Windows**, così da poterlo usare in modo più diretto senza dover avviare manualmente lo script Python.

### Branding aggiornato
È stato integrato il nuovo logo ufficiale di **NetSentinel**, in linea con l’identità del progetto e con il nuovo layout dell’applicazione.

### Mappa di rete migliorata
Una delle aggiunte più utili è la parte visuale.  
Oltre alla lista classica dei dispositivi, adesso è possibile costruire una vera e propria mappa della rete, con nodi spostabili e collegamenti tra apparati.

La mappa consente di:

- caricare uno sfondo
- trascinare i nodi
- creare collegamenti principali e secondari
- rimuovere le linee
- aprire il dettaglio di uno switch con doppio click

### Finestra dettaglio switch
Ogni dispositivo può aprire una finestra dedicata, utile per avere a portata di mano alcune operazioni rapide.

Sono presenti:

- una sezione **SSH**
- campi per credenziali
- area terminale per output e comandi
- pulsanti rapidi per alcuni comandi comuni
- una tab **SNMP** predisposta per sviluppi futuri

### Salvataggio configurazione
La posizione dei nodi, i collegamenti e l’eventuale sfondo caricato vengono salvati in locale, così da ritrovare la propria mappa anche alle aperture successive.

### Logging errori
Per facilitare troubleshooting e debug, l’app registra eventuali errori in un file locale dedicato.

---

## Come funziona il monitoraggio

NetSentinel controlla la raggiungibilità dei dispositivi provando connessioni TCP su alcune porte comunemente utilizzate, come:

- `22`
- `23`
- `80`
- `443`

In base al risultato del controllo, ogni apparato viene mostrato come:

- `🟢 ONLINE`
- `🔴 OFFLINE`
- `⚪ IN ATTESA`

In pratica, l’app non si limita a una vista statica, ma aggiorna in modo dinamico lo stato dei dispositivi sia nella lista che nella mappa.

---

## Funzionalità principali

- monitoraggio locale di dispositivi LAN
- lista switch con IP, nome, descrizione, stato e ultimo controllo
- avvio e stop del monitoraggio tramite **GO / STOP**
- aggiunta e rimozione dispositivi
- mappa di rete interattiva
- drag & drop dei nodi
- collegamenti visuali tra apparati
- finestra di dettaglio con accesso SSH
- comandi rapidi integrati
- salvataggio configurazione
- logging degli errori
- utilizzo offline senza dipendenze da servizi esterni

---

## Tecnologie utilizzate

Il progetto è sviluppato principalmente con:

- **Python**
- **Tkinter**
- **ttk**
- **Paramiko**
- **Pillow (PIL)**

---

## Struttura del progetto

```text
NetSentinel/
│
├── monitor_switches_c.py
├── netsentinel_logo.png
├── netsentinel_map_positions.json
├── netsentinel_error.log
├── NetSentinel.spec
├── NetSentinel.bat
└── README.md

Avvio da Python

Per eseguire il progetto da sorgente:

pip install paramiko pillow
python monitor_switches_c.py

Build dell’eseguibile Windows

Per generare il file .exe è possibile usare PyInstaller.

pyinstaller NetSentinel.spec
Certificato e verifica firma

Se utilizzi la versione firmata dell’eseguibile, sulla macchina Windows potrebbe essere necessario importare il certificato.

Import certificato

Posizionare il file .cer in:

C:\Cert\NetSentinel.cer

Poi eseguire da PowerShell:

Import-Certificate -FilePath "C:\Cert\NetSentinel.cer" -CertStoreLocation "Cert:\LocalMachine\Root"
Import-Certificate -FilePath "C:\Cert\NetSentinel.cer" -CertStoreLocation "Cert:\LocalMachine\TrustedPublisher"
Verifica firma
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe" verify /pa "C:\Tools\NetSentinel\NetSentinel.exe"

NetSentinel nasce da un’esigenza molto concreta: avere uno strumento semplice, locale e immediato per il monitoraggio operativo della rete, senza appoggiarsi per forza a soluzioni più pesanti o centralizzate.

Non vuole sostituire piattaforme enterprise o sistemi NMS completi.
Vuole fare bene una cosa precisa: offrire una vista rapida, chiara e utile dello stato della rete, con un approccio pratico e diretto.

Roadmap

Il progetto può essere ampliato ancora molto.
Tra le possibili evoluzioni future:

interrogazioni SNMP reali

inventario porte e MAC address

esportazione report

polling configurabile

gestione credenziali più strutturata

dashboard più dettagliata

supporto multi-device più esteso

Stato del progetto

NetSentinel è un progetto in evoluzione, costruito passo dopo passo con l’idea di trasformare uno strumento semplice in una piccola utility sempre più utile per attività IT quotidiane.

Autore

Giovanni Pirozzi / Viperhack89
