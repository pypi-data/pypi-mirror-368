# Documentation du Package d'extensions à MkDocs DSFR

Ce document fournit une vue d'ensemble complète du package d'extensions MkDocs, y compris les détails sur chaque
extension, la structure du projet, l'utilisation de uv, et les instructions pour l'installation et le développement.

## Structure du Projet

- `dsfr_structure/`: Dossier racine du package.
  - `extension/`: Contient les différentes extensions.
    - `blockquote/`: Extension pour les blockquotes.
      - `__init__.py`: Contient la logique de l'extension de blockquote.
    - `table/`: Extension pour les tables.
      - `__init__.py`: Contient la logique de l'extension de table.
    - ... (autres extensions comme `accordion`, `badge`, `tile`, etc.)
    - `all_extensions.py`: Fichier pour enregistrer toutes les extensions.
  - `tests/`: Contient les tests unitaires pour les extensions.
  - `pyproject.toml`: Fichier de configuration uv pour le package.

## Utilisation de uv

- **Commandes Principales :**
  - `uv build`: Pour construire le package.
  - `uv run pytest`: Pour exécuter les tests unitaires.

## Notes de version

### 0.7.0

- Ajout du composant [contenus médias](https://www.systeme-de-design.gouv.fr/version-courante/fr/composants/contenu-medias), vidéo uniquement à ce jour
- Corrections pour l'accessibilité

### 0.6.1

-  Card : Bug d'affichage pour une carte sans image

### 0.6.0

- Ajout de la [mise en avant](https://www.systeme-de-design.gouv.fr/version-courante/fr/composants/mise-en-avant)
- Ajout de la [citation](https://www.systeme-de-design.gouv.fr/version-courante/fr/composants/citation)

### 0.5.2

- Les alertes DSFR peuvent contenir des blocks MD (listes à puces par exemple)

### 0.5.1

- Parser interne YAML plus permissif pour l'extension Markdown sur les emojis : pymdownx.emoji.

### 0.5.0

- Ajout du [bandeau d'information importante](https://www.systeme-de-design.gouv.fr/composants-et-modeles/composants/bandeau-d-information-importante/)
- Ajout de l'option 'markup' pour alertes, cartes et tuiles, pour choisir le niveau de titre
- Bug : Suppression du paramètre "new" pour Alert
- Bug : Correction des chemins pour les artworks dans les Tiles

### 0.4.0

- Ajout des Tile, Card et et système de grille
- Remplacement des titres h3 par h5 dans les composants DSFR

### 0.3.0

- Ajout de la prise en charge des badges, tuiles, et grille (ligne, colonne) DSFR.

### 0.2.0

- Accordéons avec la syntaxe :

```
/// accordion | Titre
Contenu
///
```

### 0.1.0

- Version initiale
- Tableaux DSFR et blocs de citation
