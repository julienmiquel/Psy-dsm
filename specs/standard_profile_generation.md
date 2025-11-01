# Feature: Standard Profile Generation

## Description

This feature allows users to generate a clinical character profile by providing a detailed text description of a character. The system will analyze the description and produce a comprehensive profile that includes a DSM-5 diagnosis and a Holland Code (RIASEC) assessment.

## User Interface

The UI will consist of a large text area where the user can input the character description. Below the text area, a "Generate Profile" button will trigger the analysis.

## Workflow

1. The user enters a character description into the text area.
2. The user clicks the "Generate Profile" button.
3. The application sends the description to the Gemini API.
4. The API returns a `CharacterProfile` object.
5. The application displays the profile in a structured and easy-to-read format.

## Error Handling

- If the user clicks "Generate Profile" without entering a description, the UI will display an error message.
- If the Gemini API returns an error, the UI will display a user-friendly error message.
