# DSM-5 Character Profile Generator

This application uses the Google Gemini API to generate a clinical profile of a fictional character based on a user-provided description. The profile is based on the DSM-5 criteria and is intended for creative and academic purposes.

## How to Run

1.  **Install the dependencies:**

    ```
    poetry install
    ```

2.  **Set your Google API key:**

    ```
    export GOOGLE_API_KEY="YOUR_API_KEY"
    ```

3.  **Run the application:**

    ```
    poetry run mesop src/app/main.py
    ```

## Clinical Understanding of Psychopathy

"Psychopathy" is a psychological construct defined by a specific cluster of personality traits and behaviors. It is characterized by a combination of interpersonal, affective (emotional), and behavioral deficits.
It is fundamentally a Personality Disorder, meaning it represents an enduring, pervasive, and inflexible pattern of inner experience and behavior that deviates from cultural expectations and causes distress or impairment.

### Core Components of Psychopathy

The traits are often grouped into two main factors:

1.  **Interpersonal & Affective (Emotional) Deficits:**
    *   Glibness/Superficial Charm: Can be engaging and verbally skilled.
    *   Grandiose Sense of Self-Worth: A narcissistic and inflated view of their own abilities and importance.
    *   Pathological Lying: Lies easily and skillfully to achieve their goals.
    *   Conning/Manipulative: Uses others as tools, with no regard for their feelings.
    *   Lack of Remorse or Guilt: Does not feel bad about harming others.
    *   Shallow Affect: Experiences a very limited range of emotions; "blunted" or "shallow."
    *   Callousness / Lack of Empathy: An inability to understand or share the feelings of others.
    *   Failure to Accept Responsibility: Always blames others or rationalizes their harmful actions.

2.  **Behavioral & Lifestyle Deficits:**
    *   Need for Stimulation / Prone to Boredom: Seeks constant excitement, often through risky or harmful behavior.
    *   Impulsivity: Acts on a whim without thinking through consequences.
    *   Irresponsibility: Fails to honor commitments (work, financial, personal).
    *   Poor Behavioral Controls: Short-tempered; "hot-headed."
    *   Early Behavioral Problems: A history of conduct issues as a child.
    *   Criminal Versatility: Often engages in many different types of criminal or antisocial acts.

### Critical Distinction: Psychopathy vs. Psychosis

This is the most common point of confusion.

*   **Psychosis (like in Schizophrenia):** This is a loss of contact with reality. A psychotic person may have hallucinations (seeing/hearing things that aren't there) or delusions (fixed false beliefs, e.g., "Aliens are controlling my thoughts"). They are "ill" in the traditional sense.
*   **Psychopathy (a Personality Construct):** This is not a loss of contact with reality. A person with psychopathy is fully "in touch" with reality. They know right from wrong, but they do not care about the "wrong" part if it conflicts with their desires. Their deficit is in empathy and conscience, not in reality testing.

### "Where It Stands": How Psychopathy Presents on a Mental Status Exam (MSE)

A person with high psychopathic traits would likely present very differently from the depressed patient example. Here is a possible MSE:

*   **1. Appearance:** Often well-groomed, neat, may be "slick" or superficially charming in their appearance.
*   **2. Behavior:** Relaxed, calm. May have overly intense or "predatory" eye contact. Can seem too comfortable given the situation.
*   **3. Attitude:** Superficially cooperative, glib, and charming. May become irritable, contemptuous, or hostile if they feel challenged or are not getting what they want.
*   **4. Speech:** Normal rate, rhythm, and volume. Often articulate.
*   **5. Mood:** Reports "Good," "Fine," or "Euthymic," even when discussing negative or harmful life events.
*   **6. Affect:** Shallow or restricted. The key finding is often incongruence—they may smile or seem unbothered when describing a violent act or a major loss.
*   **7. Thought Process:** Linear, logical, and goal-directed. They are often intelligent and can be very articulate.
*   **8. Thought Content:**
    *   **Delusions:** No, not in the psychotic sense. However, their thought content is dominated by grandiose themes (how smart they are, how they've outwitted others).
    *   **Ideation:** Will deny suicidal ideation. May deny homicidal ideation but will openly blame others for their problems (e.g., "He got what he deserved").
    *   **Remorse:** Conspicuously absent. They rationalize all harmful behavior.
*   **9. Perception:** Normal. No hallucinations or illusions.
*   **10. Cognition:** Alert and oriented. Memory and concentration are typically intact and may even be sharp.
*   **11. Insight:** Extremely poor. They genuinely do not believe anything is wrong with their way of thinking or behaving. They see the problem as being with everyone else.
*   **12. Judgment:** Extremely poor. Despite potential high intelligence, their decisions are self-serving, impulsive, and fail to consider long-term consequences or the impact on others.
