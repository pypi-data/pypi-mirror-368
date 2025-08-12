import os
import sys
import re

IGNORED_DIRS = {"venv", "__pycache__", "migrations", ".git", "env", ".idea"}

def find_django_apps(project_path):
    """
    Parcourt la structure du projet et retourne une liste des noms des applications Django.
    Une app Django est détectée par la présence d'un fichier apps.py contenant AppConfig.
    """
    apps = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        if "apps.py" in files:
            app_name = os.path.basename(root)
            apps.append(app_name)
    return apps


def create_structure(project_path, apps):
    """
    Crée les dossiers templates et static avec la structure demandée.
    """
    templates_path = os.path.join(project_path, "templates")
    static_path = os.path.join(project_path, "static")

    os.makedirs(templates_path, exist_ok=True)
    os.makedirs(static_path, exist_ok=True)

    # --- TEMPLATES ---
    for app in apps:
        app_template_dir = os.path.join(templates_path, app)
        os.makedirs(app_template_dir, exist_ok=True)
        html_file = os.path.join(app_template_dir, "index.html")
        if not os.path.exists(html_file):
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(f"<!-- Template for {app} -->\n")

    # --- STATIC ---
    static_subfolders = ["css", "js", "assets"]
    for folder in static_subfolders:
        folder_path = os.path.join(static_path, folder)
        os.makedirs(folder_path, exist_ok=True)

        for app in apps:
            app_folder_path = os.path.join(folder_path, app)
            os.makedirs(app_folder_path, exist_ok=True)

            if folder == "assets":
                images_path = os.path.join(app_folder_path, "images")
                os.makedirs(images_path, exist_ok=True)


def main():
    if len(sys.argv) < 2:
        project_path = os.getcwd()
    else:
        project_path = sys.argv[1]

    if not os.path.exists(project_path):
        print(f"❌ Le chemin '{project_path}' n'existe pas.")
        sys.exit(1)

    print(f"🔍 Recherche des applications Django dans : {project_path}")
    apps = find_django_apps(project_path)

    if not apps:
        print("⚠️ Aucune application Django trouvée.")
        sys.exit(0)

    print(f"📦 Applications trouvées : {', '.join(apps)}")
    create_structure(project_path, apps)
    print("✅ Structure templates et static générée avec succès !")


if __name__ == "__main__":
    main()
