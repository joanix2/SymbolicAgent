#!/bin/bash

set -euo pipefail

SCREENSHOT_FILE="/tmp/screenshot_symbol_editor.png"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Nettoyage ancien fichier
rm -f "$SCREENSHOT_FILE"

# Capture interactive d'une zone
if gnome-screenshot -a -f "$SCREENSHOT_FILE"; then
    echo "Capture d'écran réussie : $SCREENSHOT_FILE"
else
    echo "Erreur lors de la capture d'écran ou capture annulée."
    exit 1
fi

# Vérifie que le fichier a bien été créé et n'est pas vide
if [ ! -s "$SCREENSHOT_FILE" ]; then
    echo "Le fichier de capture est vide ou inexistant."
    exit 1
fi

# Passe le chemin de l'image via pipe au script Python
echo "$SCREENSHOT_FILE" | python3 "$SCRIPT_DIR/main.py"