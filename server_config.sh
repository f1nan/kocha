#!/usr/bin/env bash
#
# Beispiel-Script zur Konfiguration einer Hostmaschine fuer den
# KOCHA-Server

HOST=$(hostname)
PORT=9999
PYTHON3=$(which python3)
CMD="$PYTHON3 -m kocha.server $HOST $PORT"

# Eingehende Anfragen ueber TCP/IP auf Port erlauben
sudo ufw allow proto tcp from any to any port "$PORT"

# Um die Regel wieder aufzuheben, nachstehenden Befehl ausfuehren
#sudo ufw delete allow proto tcp from any to any port $PORT

# Falls noch nicht vorhanden, cron-job einrichten, der den KOCHA-Server
# beim Booten startet
sudo crontab -l 2>/dev/null | grep "@reboot $CMD" >/dev/null
if [[ $? == 1 ]]; then
    sudo crontab -l 2>/dev/null; echo "@reboot $CMD" | sudo crontab -
fi

# KOCHA-Server jetzt starten
$CMD 2>/dev/null &