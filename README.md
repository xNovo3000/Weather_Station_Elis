# Weather Station

- NB: scrivere qui un resoconto di tutte le modifiche

### 13 Luglio 2021
- Vodafone adesso va fino alla data di oggi per ricevere i dati
- Risolto un problema con il logger
- Risulto un problema con il client outdoor
- Rimosso ufficialmente il branch gmove perché G-move se ne occuperà di persona

### 1 Luglio 2021
- Inserito l'account e prove finali
- Inseriti i nuovi token

### 30 Giugno 2021
- Iniziata la costruzione del sistema di transmissione dati di Vodafone migliorato

### 23 Giugno 2021
- Risolto un problema con AbstractSensor e AbstractClient: adesso se c'è un errore vengono subito interrotti e non attendono più che termini il wait del thread
- Aggiornato Vodafone con i nuovi token di Thingsboard
- Adesso i logger sono a livello 10 e non più 20

### 22 Giugno 2021
- La crowd cell adesso può prendere indoor oppure outdoor
- Adesso vengono caricati sia i risultati di Vodafone indoor che quelli outdoor

### 20 Giugno 2021
- Aggiunto un sistema in grado di scansionare la temperatura della CPU

### 15 Giugno 2021
- Sembra andare tutto bene, è un miracolo
- Aggiornata la codebase dal master
- La venv non era attiva (grazie PyCharm)

### 11 Giugno 2021
- Aggiunta la possibilità di disabilitare determinati sensori dai file json

### 9 Giugno 2021
- Terminata la base per il client Vodafone
- Necessita dei test per capire se va bene o meno
- I test devono durare due settimane minimo

### 7 Giugno 2021
- Definizione dei nuovi KPI grezzi da inviare a Thingsboard
- Branch allienato alla versione 1.2

### 3 Giugno 2021
- Nuovo logger basato su logging (retrocompatibile >=1.0 <1.2)
- Migliorato il sistema di gestione degli errori

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