# SymbolicAgent

## CLI — Exemple Discord

Détecter un template et sauvegarder la capture annotée :
```bash
source .venv/bin/activate
python -m src.workers.actions.cli find assets/discord_template.png --threshold 0.85 --save-annotated /tmp/detection_result.png
```

Vérifier visuellement le résultat :
```bash
eog /tmp/detection_result.png
```

Cliquer sur l'icône détectée :
```bash
python -m src.workers.actions.cli click-template assets/discord_template.png --threshold 0.85
```