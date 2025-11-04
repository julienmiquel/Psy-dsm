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

### Future Improvements

Here is a list of potential improvements for the application, based on the current state of the codebase:

#### 1. Data Model and Storage

*   **Optimize User-Character Mapping:** The current method for retrieving a user's characters is inefficient. The `character_index.json` should be extended to include the `user_id` for each character, or a new `user_index` should be created to map users to their characters. This will avoid the need to read every profile file to determine ownership.
*   **Refactor Cloud Storage Services:** The `datastore_service.py` and `firestore_service.py` should be refactored to use the centralized character index design, similar to the `local_file_service.py`. This will ensure consistency and scalability across different storage backends.
*   **Improve Database Error Handling:** Implement more robust error handling in the database services to gracefully handle issues like file not found, permission errors, and database connection problems.

#### 2. Application Logic and UI

*   **Structured State Management:** As the application grows in complexity, consider adopting a more structured state management library or pattern to make the session state easier to manage and debug.
*   **Enhance UI/UX:**
    *   Improve the design of the profile comparison feature to be more interactive and visually appealing.
    *   Refine the overall layout and user flow to improve the user experience.
*   **Graceful Error Display:** Instead of raising exceptions that can crash the application, catch errors (e.g., when the generative model fails) and display user-friendly error messages in the UI.

#### 3. Code Quality and Maintainability

*   **Externalize Configuration:** Move hardcoded configuration values, such as model IDs and system prompts, to external configuration files (e.g., YAML or JSON) to make them easier to manage and modify.
*   **Expand Test Coverage:** Increase the unit and integration test coverage to improve code quality, prevent regressions, and ensure the reliability of the application.
*   **Improve Modularity:** Refactor the `main.py` file by breaking it down into smaller, more focused modules to improve code organization and maintainability.

#### 4. Security

*   **Implement Secure Authentication:** Replace the current basic authentication with a more secure system, such as OAuth 2.0 or JWT-based authentication.
*   **Sanitize User Input:** Implement input sanitization to protect against potential security vulnerabilities, such as injection attacks.