# Scénario de Démonstration Vidéo (5-10 min)

Ce document sert de guide pour l'enregistrement de la vidéo de présentation du projet.

## 1. Introduction (30 sec)
**Visuel** : Page de Login.
**Audio** :
- Présenter les membres du trinôme.
- Expliquer le contexte : "Une application pour gérer les examens de 13 000 étudiants, optimiser les salles et éviter les conflits."
- Mentionner la stack : PostgreSQL + Python/Streamlit.

## 2. Rôle ADMIN - Le Cœur du Système (3 min)
**Action** : Se connecter avec `admin@umbb.dz` / `admin123`.
**Visuel** : Dashboard Admin.
**Points à montrer** :
1. **KPIs** : Montrer les compteurs (stats globales) en haut.
2. **Génération** : 
   - Aller dans la section "Génération".
   - Sélectionner une date (ex: Juin 2026).
   - Cliquer sur "Lancer la Génération".
   - Montrer la barre de progression.
   - Montrer le résultat (Tableau des examens générés).
3. **Optimisation** :
   - Expliquer que l'algo vérifie les conflits.
   - Montrer l'onglet "Audit & Qualité" : Vérifier qu'il y a 0 conflit critique.

## 3. Rôle CHEF DE DÉPARTEMENT - Validation (1 min 30)
**Action** : Se déconnecter, se connecter avec un compte CHEF (ou simuler).
*Note : Si vous n'avez pas de compte chef sous la main, montrez la section "Validation Pédagogique" dans l'interface.*
**Points à montrer** :
- Réception de l'emploi du temps proposé par l'admin.
- Possibilité de valider ou rejeter pour modification.

## 4. Rôle ÉTUDIANT - Consultation (1 min)
**Action** : Se connecter avec un compte étudiant (ou montrer la vue publique).
**Visuel** : Planning personnalisé.
**Points à montrer** :
- L'étudiant ne voit QUE ses examens.
- Filtre par date.
- Export PDF (cliquer sur le bouton téléchargement).

## 5. Rôle DOYEN - Vue Stratégique (1 min)
**Action** : Login `doyen@umbb.dz`.
**Visuel** : Graphiques globaux.
**Points à montrer** :
- Taux d'occupation des salles.
- Charge des professeurs (vérifier l'équité).

## 6. Conclusion (30 sec)
**Visuel** : Retour sur le code (VS Code) ou schéma BDD.
**Audio** :
- "Nous avons respecté les contraintes 3FN."
- "L'application est performante (temps de réponse < 1s)."
- "Merci de votre attention."
