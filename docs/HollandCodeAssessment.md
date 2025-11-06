# Documentation du Modèle `HollandCodeAssessment` (RIASEC)

Ce document décrit le modèle de données `HollandCodeAssessment`, la théorie psychométrique sur laquelle il repose, et la manière dont l'application génère les résultats via l'intelligence artificielle.

---

### 1. La Théorie : Le Modèle RIASEC de John Holland

Le modèle RIASEC, également connu sous le nom de "Holland Codes", est une théorie sur les carrières et les choix vocationnels développée par le psychologue John Holland. La théorie postule qu'il existe six grands types de personnalité professionnelle, et que la plupart des gens peuvent être classés comme une combinaison de ces six types.

Les six types sont :

1.  **Réaliste (R - Realistic)** : Les personnes pragmatiques qui aiment travailler avec des objets, des machines, des outils. Elles sont souvent douées pour des tâches manuelles et mécaniques.
2.  **Investigateur (I - Investigative)** : Les personnes analytiques et curieuses qui aiment observer, apprendre, et résoudre des problèmes complexes, souvent dans les domaines scientifiques ou mathématiques.
3.  **Artistique (A - Artistic)** : Les personnes créatives, imaginatives et non conventionnelles qui s'épanouissent dans des situations non structurées où elles peuvent utiliser leur imagination et leur créativité.
4.  **Social (S - Social)** : Les personnes qui aiment travailler avec les autres pour les aider, les former, les soigner. Elles sont souvent empathiques et douées pour la communication.
5.  **Entreprenant (E - Enterprising)** : Les personnes ambitieuses et énergiques qui aiment diriger, persuader et vendre. Elles sont souvent attirées par des rôles de leadership et de gestion.
6.  **Conventionnel (C - Conventional)** : Les personnes organisées, précises et qui aiment travailler avec des données et des règles établies. Elles excellent dans des tâches qui demandent de l'ordre et de la rigueur.

La théorie soutient que les individus sont plus satisfaits et réussissent mieux dans des environnements de travail qui correspondent à leur type de personnalité.

---

### 2. L'Objectif du Modèle de Données `HollandCodeAssessment`

Le modèle Pydantic `HollandCodeAssessment` est conçu pour structurer les résultats d'une évaluation basée sur la théorie RIASEC. Son but est de capturer de manière standardisée les informations clés d'un profil d'intérêts professionnels.

Il est intégré dans le `CharacterProfile` principal et contient les champs suivants :

-   `riasec_scores`: Une liste d'objets `HollandCode`, où chacun contient :
    -   `theme`: Le nom du type RIASEC (ex: "Social").
    -   `score`: Un score numérique (généralement de 1 à 10) représentant l'affinité du personnage pour ce thème.
    -   `description`: Une brève explication du thème.
-   `top_themes`: Une liste des 2 ou 3 thèmes les plus dominants pour le personnage (ex: `["Social", "Artistic"]`).
-   `summary`: Une synthèse narrative qui interprète le profil global, explique comment les thèmes dominants interagissent et suggère des pistes professionnelles.

---

### 3. Fonctionnement du Prompt

L'évaluation `HollandCodeAssessment` n'est pas calculée par une formule, mais **générée par une intelligence artificielle (Gemini Pro)**. Voici comment cela fonctionne :

1.  **Le Rôle Assigné** : Le `SYSTEM_PROMPT` (situé dans `src/app/services.py`) donne à l'IA l'instruction de se comporter comme un "psychologue clinicien et conseiller d'orientation".
2.  **L'Analyse du Texte** : L'IA reçoit la description textuelle du personnage fournie par l'utilisateur.
3.  **La Structure JSON** : Le prompt inclut un schéma JSON strict que l'IA doit obligatoirement suivre pour sa réponse. Ce schéma contient la structure exacte du `HollandCodeAssessment`.
4.  **La Génération** : En se basant sur son analyse du texte, l'IA remplit le schéma JSON. Elle attribue des scores à chaque thème RIASEC, identifie les thèmes dominants, et rédige une synthèse, simulant ainsi l'interprétation qu'un expert humain pourrait faire.

Ce processus permet de transformer une description narrative en une analyse psychométrique structurée et directement exploitable par l'application.
