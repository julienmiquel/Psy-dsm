# Feature: Chat-Based Profile Generation

## Description

This feature provides an interactive, conversational interface for generating a clinical character profile. Users can chat with an AI agent, which will ask clarifying questions to gather the necessary information for the profile.

## User Interface

The UI will be a chat interface with a text input for the user's messages and a display area for the conversation history.

## Workflow

1. The user enters a message in the chat input.
2. The application sends the message to the `google-adk` `LlmAgent`.
3. The agent responds with either a clarifying question or a complete `CharacterProfile` object.
4. If the agent asks a question, the user can continue the conversation.
5. If the agent returns a `CharacterProfile`, the application will display the profile in the UI.

## Error Handling

- If the `LlmAgent` returns an error, the UI will display a user-friendly error message.
