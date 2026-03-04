-- Migration: Renommer 'Champagne' en 'Effervescents' dans la table bottles
-- À exécuter sur la base de données SQLite

UPDATE bottles SET type = 'Effervescents' WHERE type = 'Champagne';