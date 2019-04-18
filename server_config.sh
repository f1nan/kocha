#!/usr/bin/env bash
#
# Beispiel-Script zur Konfiguration einer Hostmaschine fuer den
# KOCHA-Server
#

HOST=$(hostname)
PORT=9999
PYTHON3=$(which python3)

# Eingehende Anfragen ueber TCP/IP auf Port erlauben
sudo ufw allow proto tcp from any to any port $PORT

# Um die Regel wieder aufzuheben, nachstehenden Befehl ausfuehren
#sudo ufw delet allow proto tcp from any to any port $PORT

# cron-job einrichten, der den KOCHA-Server beim Booten startet
sudo crontab -l 2>/dev/null | echo "$PYTHON3 kocha.server $HOST $PORT" | crontab -