import os
from pathlib import Path

# Les seeders du projet: les données de démonstration.
#
# Auto-découverte, comme pour les modèles, les controllers et les services:
# `from app.seed import *` (dans app/__init__.py) importe tous les modules du
# dossier. Et comme chaque `class XxxSeed(Seedable)` s'enregistre au moment où
# Python lit sa déclaration (voir Seedable.__init_subclass__), l'import suffit.
#
# Donc pour ajouter un jeu de données: créer un fichier ici, hériter de Seedable,
# implémenter seed(). Aucune liste à mettre à jour, aucun import à ajouter.

# Avec pathlib
path = Path(__file__).parent.absolute()
__all__ = [
    f.name[:-3] for f in path.iterdir() if f.is_file() and f.name.endswith(".py")
]

# Mot de passe commun aux comptes de démonstration, variable SEED_PASSWORD (.env).
DEMO_PASSWORD = os.environ.get("SEED_PASSWORD", "change-me")

ROLES = ["CLIENT", "TECHNICIEN", "ADMIN"]
USERS = [
    (
        "admin",
        "admin@example.com",
        DEMO_PASSWORD,
        "admin",
        "admin",
        None,
        None,
        ["CLIENT", "ADMIN"],
    ),
    ("test", "test@example.com", DEMO_PASSWORD, "test", "test", None, None, ["CLIENT"]),
    (
        "technicien_1",
        "technicien1@example.com",
        DEMO_PASSWORD,
        "Technicien",
        "Un",
        None,
        None,
        ["TECHNICIEN"],
    ),
    (
        "technicien_2",
        "technicien2@example.com",
        DEMO_PASSWORD,
        "Technicien",
        "Deux",
        None,
        None,
        ["TECHNICIEN"],
    ),
    (
        "technicien_3",
        "technicien3@example.com",
        DEMO_PASSWORD,
        "Technicien",
        "Trois",
        None,
        None,
        ["TECHNICIEN"],
    ),
]

# Seeding data for categories: (name, description)
CATEGORIES = [
    (
        "Hardware & Workstations",
        (
            "Laptops, desktops, monitors, docking stations, keyboards, and "
            "office peripherals."
        ),
    ),
    (
        "Software & Applications",
        (
            "Issues with ERP system, logistics tools, Microsoft 365,"
            " application crashes, and install requests."
        ),
    ),
    (
        "Network & Connectivity",
        (
            "Wi-Fi disconnects, VPN remote access, local network issues, and"
            " warehouse internet drops."
        ),
    ),
    (
        "User Accounts & Access",
        (
            "Password resets, Active Directory account creation, permission"
            " requests, and new employee onboarding."
        ),
    ),
    (
        "Printers & Warehouse Scanners",
        (
            "Shipping label printers, barcode scanners, office multi-function"
            " printers, and paper jams."
        ),
    ),
]

# Seeding data for priorities: (name, level, delay_hours)
PRIORITIES = [
    ("Low", 1, 48),
    ("Medium", 2, 24),
    ("High", 3, 8),
    ("Urgent", 4, 2),
]

SITES = [
        ("Technobel", "Place de l'univeristé, 15", "Louvain-La-Neuve", ["admin", "test"] , [])
    ]