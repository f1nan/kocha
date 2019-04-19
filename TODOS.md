# TODOS

- [x] Es muss ein Datentransferobjekt im JSON-Format fuer die Kommunikation von Server und Client geben
    - [x] Eigenschaften: content (string), send_at (datetime), sender (string), is_dm (bool)

- [x] Es muss ein Client-Prgramm geben
    - [x] Der Client muss ueber TCP/IP mit dem Server kommunizieren koennen
        - [x] Daten vom Server muessen empfangen werden koennen
        - [x] Daten muessen zum Server geschickt werden koennen
    - [x] UI mit curses bauen
        - [x] Das UI muss sich bei Groeßenaenderung des Terminals ebenfalls anpassen
        - [x] Es muss eine Titelzeile mit dem Namen und der Version des Programms geben
        - [x] Es muss ein Nachrichtenfenster fuer die empfangenen Nachrichten geben
            - [x] Empfangene Nachrichten muessen im Nachrichtenfenster erscheinen; dabei darf die Eingabe von Text nicht gestoert werden
            - [x] Bei Erwaehnung des eigenen Alias muss dieser farblich hervorgehoben werden
            - [x] Persoenliche Nachrichten muessen farblich hervorgehoben werden
        - [x] Es muss eine Eingabezeile fuer Text geben
            - [x] Zu langer Text muss am Zeilenanfang abgeschnitten werden, sodass der Schreibprozess nicht gestoert wird
            - [x] Beim Druecken von Enter muss der Text im Nachrichtenfenster erscheinen und die Eingabezeile muss geleert werden
            - [x] Die Pfeiltasten muessen deaktiviert werden
            - [x] Die Ruecktaste muss wie erwartet funktionieren
            - [x] Nur ASCII-Zeichen als Eingabe erlauben um Probleme mit falschem Encoding durch curses zu umgehen

- [x] Es muss ein Server-Programm geben
    - [x] Clients muessen sich mit einem Alias am Server anmelden koennen
        - [x] Wenn ein Alias bereits verwendet wird, darf die Anmeldung nicht funktionieren
    - [x] Server muss oeffentliche Nachrichten im Chat an alle Clients broadcasten koennen
    - [x] Server muss persoenliche Nachrichten nur an den adressierten Empfaenger weiterleiten koennen
    - [x] Server muss eine Liste der verfuegbaren Kommandos zurueck geben koennen
    - [x] Server muss eine Liste der angemeldeten Clients zurueck geben koennen
    - [x] Server muss mehrere Clients gleichzeitig bedienen koennen
    - [x] Server muss beim "shutdown" alle Clien-Threads terminieren
    - [x] Server muss andere Nutzer informieren, wenn ein neuer Nutzer den Chat betritt oder verlaesst

- [ ] Installation
    - [ ] Installation des Servers
        - [ ] Server muss beim Starten des Computers mitgestartet werden (cron?)
        - [x] Port des Servers muss konfigurierbar sein
    - [x] Installation des Clients
        - [x] IP-Adresse und Port des Servers muessen einstellbar sein

- [ ] Allgemeine Aufgaben
    - [ ] README ueberarbeiten
    - [x] Lizenz hinzufuegen
