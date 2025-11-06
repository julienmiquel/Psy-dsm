# Documentation du Modèle `CHCModel` (Cattell-Horn-Carroll)

Ce document décrit le modèle de données `CHCModel`, la théorie psychométrique sur laquelle il repose, et la manière dont l'application génère les résultats via l'intelligence artificielle.

---

### 1. La Théorie : Le Modèle de Cattell-Horn-Carroll (CHC)

La théorie de Cattell-Horn-Carroll (CHC) est le modèle le plus influent et le plus complet pour comprendre les aptitudes cognitives humaines. Contrairement aux modèles RIASEC et Hexa3D qui se concentrent sur les *intérêts* professionnels, le modèle CHC se focalise sur l'intelligence et la structure des capacités mentales.

La théorie est hiérarchique et se structure en trois niveaux (ou "strates") :

-   **Strate III (le sommet)** : Le **facteur *g*** (intelligence générale), qui représente la capacité cognitive globale d'un individu.
-   **Strate II** : Les **aptitudes larges** (Broad Abilities). Il s'agit d'une dizaine de capacités générales qui constituent le facteur *g*. Les plus connues incluent :
    -   **L'intelligence fluide (*Gf*)** : La capacité à raisonner et à résoudre de nouveaux problèmes.
    -   **L'intelligence cristallisée (*Gc*)** : Les connaissances acquises par l'expérience et la culture.
    -   **La mémoire à court terme (*Gsm*)** : La capacité à retenir et à manipuler des informations pendant une courte période.
    -   **Le traitement visuel (*Gv*)** : La capacité à percevoir et à manipuler des motifs visuels.
-   **Strate I (la base)** : Les **aptitudes spécifiques** (Narrow Abilities). Chaque aptitude large se décompose en de nombreuses aptitudes plus spécifiques. Par exemple, l'intelligence cristallisée (*Gc*) inclut des aptitudes comme le développement du langage ou les connaissances lexicales.

Le modèle CHC est la base de la plupart des tests de QI modernes.

---

### 2. L'Objectif du Modèle de Données `CHCModel`

Le modèle Pydantic `CHCModel` est conçu pour structurer une analyse des capacités cognitives d'un personnage en se basant sur la théorie CHC. Son objectif est de fournir un profil cognitif, et non un profil d'intérêts.

Il contient les champs suivants :

-   `g_factor`: Un score numérique représentant l'intelligence générale (facteur *g*).
-   `broad_abilities`: Une liste d'objets `BroadAbility`, où chacun représente une aptitude large de la Strate II. Chaque objet contient :
    -   `id` et `name`: L'identifiant (ex: "Gf") et le nom (ex: "Fluid Intelligence") de l'aptitude.
    -   `description`: Une explication de ce que mesure cette aptitude.
    -   `score`: Le score estimé pour cette aptitude large.
    -   `evidence_summary`: Un résumé des éléments du texte qui justifient le score attribué.
    -   `narrow_abilities`: Une liste d'objets `NarrowAbility` (Strate I) qui détaillent les aptitudes spécifiques liées.
-   `poor_coverage_topics`: Une liste de domaines où le texte fourni était insuffisant pour permettre une évaluation fiable.
-   `raw_text_bloc`: Le texte original fourni par l'utilisateur.

---

### 3. Fonctionnement du Prompt

L'évaluation `CHCModel` est, comme les autres, **générée par une intelligence artificielle (Gemini Pro)**. Le processus est géré par la fonction `generate_chc_profile` dans `app/psychometry_chc_generate.py`.

1.  **Le Rôle Assigné** : Le prompt système (défini dans `app/psychometry_chc_generate.py`) demande à l'IA d'agir comme un "psychologue spécialisé en psychométrie cognitive".
2.  **L'Analyse Cognitive** : L'IA analyse le texte fourni non pas pour les intérêts, mais pour des indices sur les capacités cognitives. Par exemple, la capacité à résoudre des problèmes complexes indiquerait une intelligence fluide (*Gf*) élevée, tandis qu'un vocabulaire riche indiquerait une intelligence cristallisée (*Gc*) élevée.
3.  **La Structure Hiérarchique** : Le prompt contient un schéma JSON qui reflète la structure hiérarchique du modèle CHC. L'IA doit identifier les aptitudes larges pertinentes, les décomposer en aptitudes spécifiques, attribuer des scores, et surtout, **justifier chaque score** avec des éléments tirés du texte (`evidence_summary`).
4.  **L'Auto-Critique** : Une instruction clé du prompt est de lister les sujets pour lesquels le texte ne fournit pas assez d'informations (`poor_coverage_topics`). Cela rend l'analyse plus honnête et transparente sur ses propres limites.

Ce processus permet de générer une estimation plausible du profil cognitif d'un personnage, en se basant sur les inférences que l'on peut tirer d'un texte descriptif.
