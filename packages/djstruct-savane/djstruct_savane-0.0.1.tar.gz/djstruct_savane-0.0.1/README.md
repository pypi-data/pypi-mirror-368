# 🏗️ djstruct-savane

**djstruct-savane** est un utilitaire en ligne de commande pour **Django** qui scanne automatiquement votre projet, détecte toutes vos applications, et génère une structure complète pour vos dossiers **`templates/`** et **`static/`**.

> Plus besoin de créer manuellement vos dossiers et fichiers HTML/CSS/JS — **djstruct-savane** le fait pour vous en quelques secondes !

---

## 🚀 Fonctionnalités

- 🔍 **Détection automatique** des applications Django (sans dépendre de `INSTALLED_APPS`)
- 🚫 **Ignorance intelligente** des dossiers inutiles (`venv/`, `__pycache__/`, `migrations/`, `.git`, etc.)
- 📂 **Génération complète** de la structure :
  - `templates/{app_name}/index.html`
  - `static/css/{app_name}/`
  - `static/js/{app_name}/`
  - `static/assets/{app_name}/images/`
- ✅ Compatible **Python ≥ 3.6** et toutes versions de Django

---

## 📦 Installation

Depuis **PyPI** *(après publication)* :
```bash
pip install djstruct-savane

## 💻 Utilisation
- placez-vous à la racine de votre projet Django
- lancez simplement :

gn-djstruct

Ou précisez un chemin vers un projet :

gn-djstruct /chemin/vers/mon_projet


## 📂 Exemple de résultat

Pour un projet contenant deux applications blog et shop, l’exécution de :

templates/
│
├── blog/
│   └── index.html
│
└── shop/
    └── index.html

static/
│
├── css/
│   ├── blog/
│   └── shop/
│
├── js/
│   ├── blog/
│   └── shop/
│
└── assets/
    ├── blog/
    │   └── images/
    └── shop/
        └── images/

## 📖 Explication

templates/{app_name}/index.html → Fichier HTML principal pour chaque application
static/css/{app_name}/ → Dossier CSS dédié à l’application
static/js/{app_name}/ → Dossier JavaScript dédié à l’application
static/assets/{app_name}/images/ → Dossier pour stocker les images de l’application
Grâce à cette structure, vos assets sont organisés par application, ce qui facilite leur gestion dans les grands projets Django.

## ⚙️ Options

Sans argument → scanne le dossier courant
Avec chemin → scanne un chemin spécifique

## 🛠️ Licence

MIT © 2025 - SAVANE Mouhamed