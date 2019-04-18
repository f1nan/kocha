# TODOS

- [x] Es muss ein Datentransferobjekt im JSON-Format für die Kommunikation von Server und Client geben
    - [x] Eigenschaften: content (string), send_at (datetime), sender (string), is_dm (bool)

- [x] Es muss ein Client-Prgramm geben
    - [x] Der Client muss über TCP/IP mit dem Server kommunizieren können
        - [x] Daten vom Server müssen empfangen werden können
        - [x] Daten müssen zum Server geschickt werden können
    - [x] UI mit curses bauen
        - [x] Das UI muss sich bei Groeßenaenderung des Terminals ebenfalls anpassen
        - [x] Es muss eine Titelzeile mit dem Namen und der Version des Programms geben
        - [x] Es muss ein Nachrichtenfenster für die empfangenen Nachrichten geben
            - [x] Empfangene Nachrichten müssen im Nachrichtenfenster erscheinen; dabei darf die Eingabe von Text nicht gestoert werden
            - [x] Bei Erwaehnung des eigenen Alias muss dieser farblich hervorgehoben werden
            - [x] Persoenliche Nachrichten muessen farblich hervorgehoben werden
        - [x] Es muss eine Eingabezeile für Text geben
            - [x] Zu langer Text muss am Zeilenanfang abgeschnitten werden, sodass der Schreibprozess nicht gestört wird
            - [x] Beim Drücken von Enter muss der Text im Nachrichtenfenster erscheinen und die Eingabezeile muss geleert werden
            - [x] Die Pfeiltasten müssen deaktiviert werden
            - [x] Die Rücktaste muss wie erwartet funktionieren
            - [x] Nur ASCII-Zeichen als Eingabe erlauben um Probleme mit falschem Encoding durch curses zu umgehen

- [x] Es muss ein Server-Programm geben
    - [x] Clients müssen sich mit einem Alias am Server anmelden können
        - [x] Wenn ein Alias bereits verwendet wird, darf die Anmeldung nicht funktionieren
    - [x] Server muss oeffentliche Nachrichten im Chat an alle Clients broadcasten koennen
    - [x] Server muss persoenliche Nachrichten nur an den adressierten Empfaenger weiterleiten koennen
    - [x] Server muss eine Liste der verfuegbaren Kommandos zurueck geben koennen
    - [x] Server muss eine Liste der angemeldeten Clients zurueck geben koennen
    - [x] Server muss mehrere Clients gleichzeitig bedienen können
    - [x] Server muss beim "shutdown" alle Clien-Threads terminieren
    - [x] Server muss andere Nutzer informieren, wenn ein neuer Nutzer den Chat betritt oder verlaesst

- [ ] Installation
    - [ ] Installation des Servers
        - [ ] Server muss beim Starten des Computers mitgestartet werden (cron?)
        - [x] Port des Servers muss konfigurierbar sein
    - [x] Installation des Clients
        - [x] IP-Adresse und Port des Servers müssen einstellbar sein

- [ ] Allgemeine Aufgaben
    - [ ] README ueberarbeiten
    - [x] Lizenz hinzufuegen
