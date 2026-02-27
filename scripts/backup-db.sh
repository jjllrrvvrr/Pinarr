#!/bin/bash
# Pinarr Database Backup Script
# Usage: ./backup-db.sh [backup_name]

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backup}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
DATABASE_FILE="/data/pinarr.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="${1:-pinarr_backup_$TIMESTAMP}"

# Créer le répertoire de backup si inexistant
mkdir -p "$BACKUP_DIR"

# Vérifier que la base existe
if [ ! -f "$DATABASE_FILE" ]; then
    echo "❌ Erreur: Base de données non trouvée: $DATABASE_FILE"
    exit 1
fi

# Backup avec compression
echo "📦 Création du backup: $BACKUP_NAME.sql.gz..."
sqlite3 "$DATABASE_FILE" ".backup /tmp/backup_temp.db" 2>/dev/null || true

# Si sqlite3 backup échoue, copier directement
if [ ! -f "/tmp/backup_temp.db" ]; then
    echo "📋 Copie directe de la base..."
    cp "$DATABASE_FILE" "/tmp/backup_temp.db"
fi

# Compresser
gzip -c "/tmp/backup_temp.db" > "$BACKUP_DIR/${BACKUP_NAME}.db.gz"
rm -f "/tmp/backup_temp.db"

# Vérifier le backup
if [ -f "$BACKUP_DIR/${BACKUP_NAME}.db.gz" ]; then
    SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.db.gz" | cut -f1)
    echo "✅ Backup créé: $BACKUP_DIR/${BACKUP_NAME}.db.gz ($SIZE)"
else
    echo "❌ Erreur: Échec de la création du backup"
    exit 1
fi

# Nettoyage des vieux backups
echo "🧹 Nettoyage des backups de plus de $RETENTION_DAYS jours..."
find "$BACKUP_DIR" -name "*.db.gz" -type f -mtime +$RETENTION_DAYS -delete

echo "✨ Backup terminé avec succès!"
