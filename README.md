# Weather Station

- NB: scrivere qui un resoconto di tutte le modifiche

### 25 Maggio 2021
- Aggiunto l'autorun da 'iniettare' su systemd
- Null checks per la Crowd Cell
- Se la richiesta fallisce, la prossima avverrà dopo 60 secondi
- Aggiunto il logger per Vodafone
- Modifica ai dati da inviare a Thingsboard
- Creato il server fake in attesa dei dati da Vodafone
- Aggiunto l'autorun per la Weather Station
- Migliorato il sistema di logging sotto la scocca
- Il logger adesso ha il suo file di configurazione
- Il logger non fa più richeste bloccanti

### 18 Maggio 2021
- Gestore dei dati dalla crowd cell terminato
- TODO: creare server fasullo per testarne il corretto funzionamento

### 17 Maggio 2021
- Inizio dei lavori sul branch 'vodafone'

### 12 Maggio 2021
- Il 'master' adesso ha il codice multithread
- Testato direttamente sulla Weather Station
- Assegnato il tag 1.0
- Inizio dei lavori sul branch 'gmove'