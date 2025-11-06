# Documentation du Modèle `Hexa3DAssessment`

Ce document décrit le modèle de données `Hexa3DAssessment`, la théorie psychométrique sur laquelle il repose, et la manière dont l'application génère les résultats via l'intelligence artificielle.

---

### 1. La Théorie : Le Modèle Hexa3D

L'Hexa3D est un questionnaire d'intérêts professionnels basé sur le modèle RIASEC de Holland, mais il apporte une analyse beaucoup plus fine et multidimensionnelle. Il a été conçu pour offrir une vision plus nuancée des intérêts d'une personne en les évaluant à travers trois prismes distincts et en y ajoutant des dimensions supplémentaires.

Les trois axes d'analyse principaux sont :

1.  **Les Activités** : Quelles sont les tâches que la personne aime *faire* ? (ex: "Construire des choses", "Aider les autres").
2.  **Les Qualités** : Comment la personne se perçoit-elle ? Quelles sont les qualités qu'elle pense posséder ? (ex: "Je suis quelqu'un de créatif", "Je suis méthodique").
3.  **Les Professions** : Quels sont les métiers qui attirent la personne ? (ex: "Ingénieur", "Psychologue").

En analysant le profil RIASEC pour chacun de ces trois domaines, l'Hexa3D permet de détecter des nuances importantes. Par exemple, une personne peut être attirée par des professions *Sociales* mais préférer des activités *Investigatives*.

De plus, l'Hexa3D intègre deux dimensions "3D" qui affinent encore le profil :

-   **Prestige** : La personne est-elle attirée par des professions à statut social élevé (P+) ou plus modeste (P-) ?
-   **Genre** : Les intérêts de la personne sont-ils statistiquement plus proches des intérêts typiquement masculins ou féminins ?

---

### 2. L'Objectif du Modèle de Données `Hexa3DAssessment`

Le modèle Pydantic `Hexa3DAssessment` est conçu pour capturer la richesse et la complexité des résultats d'un test comme l'Hexa3D. Il est beaucoup plus détaillé que le `HollandCodeAssessment`.

Il est intégré dans le `CharacterProfile` principal et contient les champs suivants :

-   `assessment_datetime`: La date et l'heure de l'évaluation.
-   `profil_activites`, `profil_qualites`, `profil_professions`: Trois objets `ProfilHexaDomaine` distincts, un pour chaque axe d'analyse. Chacun contient :
    -   `notes_brutes` et `notes_etalonnees`: Les scores RIASEC pour ce domaine spécifique.
    -   `code_riasec`: Le code à trois lettres (ex: "SIA") pour ce domaine.
-   `profil_global`: Une synthèse des trois profils précédents, représentant les intérêts généraux.
-   `dimensions_secondaires`: Un objet `Dimensions3D` qui stocke les scores pour le Prestige (élevé/faible) et le Genre (masculin/féminin).
-   `code_global_top_themes`: Les 2 ou 3 thèmes dominants du profil global.
-   `niveau_differenciation_global` et `niveau_consistance_global`: Des indicateurs psychométriques sur la clarté et la cohérence du profil.
-   `summary`: Une synthèse narrative qui interprète l'ensemble des résultats.

---

### 3. Fonctionnement du Prompt

Comme pour le RIASEC, l'évaluation `Hexa3DAssessment` est **générée par une intelligence artificielle (Gemini Pro)**.

1.  **Le Rôle Assigné** : Le `SYSTEM_PROMPT_HEXA3D` (situé dans `src/app/services.py`) instruit l'IA d'agir comme un psychologue clinicien.
2.  **La Structure JSON Complexe** : Le prompt contient un schéma JSON détaillé qui correspond exactement à la structure du modèle `Hexa3DAssessment`.
3.  **La Génération Détaillée** : En analysant la description du personnage, l'IA ne se contente pas de donner un profil RIASEC unique. Elle doit décomposer son analyse pour remplir les sections `activites`, `qualites`, et `professions` séparément, générer un profil global, et évaluer les dimensions de prestige et de genre. Elle simule ainsi une analyse psychométrique multidimensionnelle, fournissant des résultats beaucoup plus riches et nuancés qu'une simple évaluation RIASEC.
