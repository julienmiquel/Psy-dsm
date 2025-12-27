# Audio Analysis Model

The `AudioAnalysisResult` model represents the output of the forensic audio analysis system. It is designed to extract deep psychological and forensic insights from audio recordings of conversations.

## Underlying Theory

### Forensic Audio Analysis
This module combines several disciplines:
1.  **Speaker Diarization**: The process of partitioning an input audio stream into homogeneous segments according to the speaker identity ("who spoke when").
2.  **Sentiment/Emotion Analysis**: Detecting the underlying emotional state (e.g., anxiety, aggression, deception) in the voice and text.
3.  **Statement Validity Analysis**: Identifying potential indicators of deception, manipulation, or "dark patterns" in communication.

### Purpose of the Model

The `AudioAnalysisResult` model serves to:
1.  **Structure Unstructured Audio**: Convert audio data into a structured transcript with metadata.
2.  **Highlight Risk Factors**: Automatically flag potential lies, manipulation (gaslighting, coercion), or high-risk emotional states.
3.  **Provide Overview**: Offer a high-level assessment of the interaction dynamics.

## Data Model

### `AudioAnalysisResult`
The root model containing the full analysis.
- `overall_assessment`: A summary of the conversation's dynamics and key findings.
- `segments`: A list of `SentenceAnalysis` objects representing the chronological flow of the conversation.

### `SentenceAnalysis`
Represents a single turn or sentence in the dialogue.
- `speaker_label`: The identified speaker (e.g., "Speaker 1", "Host").
- `text`: The verbatim transcription.
- `emotional_tone`: The detected emotion (e.g., "Defensive", "Calm").
- `dark_patterns`: A list of detected `DarkPattern` objects.

### `DarkPattern`
Represents a specific instance of manipulative or deceptive speech.
- `type`: The category of the pattern (e.g., "Gaslighting", "Lie", "Minimization").
- `description`: An explanation of why this segment was flagged.
- `confidence`: The AI's confidence level in this detection (Low, Medium, High).

## AI Generation Process

The analysis is performed by a multimodal LLM (Gemini 1.5 Pro) which can process audio natively.

1.  **Input**: Raw audio file (mp3, wav, etc.).
2.  **Prompting**: The system prompt (`SYSTEM_PROMPT_AUDIO_ANALYSIS`) instructs the model to act as a forensic psychologist.
    - It requires simultaneous transcription and analysis.
    - It specifically prompts for "dark patterns" and signs of deception.
3.  **Output**: A JSON object strictly matching the `AudioAnalysisResult` schema.
