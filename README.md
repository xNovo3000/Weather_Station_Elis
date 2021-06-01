# Weather Station

- NB: scrivere qui un resoconto di tutte le modifiche

### 1 Giugno 2021
- Riscritto il logger, adesso è basato sulla libreria logging
- Ci sono nuove opzioni per il logger, vedere Files/Configurations/SimulationLogger.json

### 29 Maggio 2021
- Rivoluzionato il sistema di gestione degli errori
- Adesso in caso di errore bloccante il programma è progettato per terminare autonomamente
- Adesso il logger ha più livelli di log
- Si può scegliere sia per terminale che per file il livello di log e se abilitarlo o meno

### 28 Maggio 2021
- Hotfix per il contatore della pioggia

### 25 Maggio 2021
- Aggiunto l'autorun per la Weather Station
- Migliorato il sistema di logging sotto la scocca
- Il logger adesso ha il suo file di configurazione
- Il logger non fa più richeste bloccanti

### 12 Maggio 2021
- Il 'master' adesso ha il codice multithread
- Testato direttamente sulla Weather Station

### 4 Maggio 2021
- Introduzione del paradigma OO in vista di future interazioni con Vodafone e GMove

### 3 Marzo 2021
- Primo prototipo Netcom