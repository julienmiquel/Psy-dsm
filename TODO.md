### Design Proposal: Profile Comparison

This design introduces a new feature to compare two profiles of the same character, generated from different input texts. This will help you track the evolution of a character's profile and understand the impact of different descriptions.

#### 1. User Interface

*   **Profile Selection for Comparison:**
    *   In the **History** sidebar, a "Compare" button will be added next to each character name.
    *   Clicking "Compare" will open a selection dialog where you can choose another version of the same character's profile to compare against.

*   **Comparison View:**
    *   A new **"Comparison"** tab will appear next to the "Generator" and "User Profile" tabs.
    *   This tab will display a side-by-side comparison of the two selected profiles, clearly highlighting the differences.

#### 2. Comparison Details

The comparison view will provide a detailed breakdown of the differences between the two profiles:

*   **Character Profile Comparison:**
    *   **Overall Assessment Summary:** A text diff will be used to visually highlight the changes in the assessment summary.
    *   **Holland Code (RIASEC) Assessment:**
        *   The two RIASEC radar charts will be displayed side-by-side for easy visual comparison.
        *   A table will show the scores for each RIASEC theme from both profiles, with the difference in scores calculated and displayed.
    *   **Diagnoses:** A table will list the diagnoses from both profiles, clearly indicating any added, removed, or modified diagnoses, including changes in criteria met or specifiers.

*   **CHC Profile Comparison:**
    *   **General Intelligence (g-factor):** The g-factor from both profiles will be shown, along with the calculated difference.
    *   **Broad and Narrow Abilities:** A table will present the scores for each broad and narrow ability from both profiles, with the differences highlighted to easily spot changes in cognitive assessment.

#### 3. Backend Implementation

*   **Comparison Service:** A new service will be created to handle the comparison logic. This service will take two profile objects (either `CharacterProfile` or `CHCModel`) and generate a structured comparison result.
*   **Database Services:** The existing database services will be enhanced to allow fetching specific versions of a character's profiles for comparison.

This design will enable you to perform a comprehensive analysis of how a character's psychological and cognitive profiles evolve based on different narratives, providing valuable insights into the character's development.