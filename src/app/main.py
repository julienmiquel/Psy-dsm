import json
import os
import time
from google import genai
from google.genai import types
from datetime import date
from typing import List, Optional, Dict, Any

# Import Pydantic
from pydantic import BaseModel, Field

import mesop as me
import mesop.labs as mel

from .models import CharacterProfile
from .services import generate_character_profile
from .agent import agent as adk_agent

from dataclasses import field

@me.stateclass
class State:
    client: Optional[genai.Client] = None
    profile: Optional[CharacterProfile] = None
    error: Optional[str] = None
    loading: bool = True
    chat_mode: bool = False
    chat_history: List[Dict[str, str]] = field(default_factory=list)

def on_load(e: me.LoadEvent):
    """Sets up the Gemini client on application load."""
    state = me.state(State)
    try:
        state.client = genai.Client()
    except Exception as e:
        state.error = f"Could not initialize Gemini client. Check your API key. Error: {e}"
    state.loading = False

@me.page(path="/", on_load=on_load)
def app():
    """Main Mesop application page."""
    state = me.state(State)
    with me.box(style=me.Style(
        display="flex",
        flex_direction="column",
        align_items="center",
        padding=me.Padding.all(20),
        gap=20,
    )):
        me.text("DSM-5 Character Profile Generator", type="headline-4")
        me.button("Toggle Chat Mode", on_click=toggle_chat_mode, type="raised")

        if state.chat_mode:
            chat_ui()
        else:
            standard_ui()

def toggle_chat_mode(e: me.ClickEvent):
    """Handles the 'Toggle Chat Mode' button click."""
    state = me.state(State)
    state.chat_mode = not state.chat_mode

def standard_ui():
    """Renders the standard UI."""
    state = me.state(State)
    if not state.client:
        me.text("Error: API client not configured.", style=me.Style(color="red"))
        return

    with me.box(style=me.Style(width="100%", max_width="800px")):
        me.textarea(
            label="Character Description",
            key="description",
            rows=10,
            style=me.Style(width="100%"),
        )
        me.button("Generate Profile", on_click=generate_profile, type="raised")

    if state.loading:
        me.progress_spinner()

        if state.error:
            me.text(f"Error: {state.error}", style=me.Style(color="red"))

        if state.profile:
            display_profile(state.profile)

def chat_ui():
    """Renders the chat UI."""
    state = me.state(State)
    if not state.client:
        me.text("Error: API client not configured.", style=me.Style(color="red"))
        return

    with me.box(style=me.Style(width="100%", max_width="800px")):
        for message in state.chat_history:
            me.text(f"**{message['role']}**: {message['content']}")
        me.input(label="Chat with the agent", key="chat_input", style=me.Style(width="100%"))
        me.button("Send", on_click=send_chat_message, type="raised")

    if state.loading:
        me.progress_spinner()

    if state.error:
        me.text(f"Error: {state.error}", style=me.Style(color="red"))

    if state.profile:
        display_profile(state.profile)

from google.adk.runners import Runner

def send_chat_message(e: me.ClickEvent):
    """Handles the 'Send' button click in chat mode."""
    state = me.state(State)
    user_input = me.get_value("chat_input")

    if not user_input:
        return

    state.chat_history.append({"role": "user", "content": user_input})
    state.loading = True
    state.error = None
    state.profile = None

    try:
        runner = Runner(agent=adk_agent)
        response = runner.run(user_input)
        if isinstance(response, CharacterProfile):
            state.profile = response
        else:
            state.chat_history.append({"role": "agent", "content": response})
    except Exception as err:
        state.error = str(err)
    finally:
        state.loading = False

def generate_profile(e: me.ClickEvent):
    """Handles the 'Generate Profile' button click."""
    state = me.state(State)
    description = me.get_value("description")

    if not description:
        state.error = "Please enter a character description."
        return

    state.loading = True
    state.error = None
    state.profile = None

    try:
        profile = generate_character_profile(description, state.client)
        state.profile = profile
    except Exception as err:
        state.error = str(err)
    finally:
        state.loading = False

def display_profile(profile: CharacterProfile):
    """Renders the character profile in the UI."""
    profile_dict = profile.model_dump()

    with me.box(style=me.Style(
        border=me.Border.all(1, "lightgrey"),
        padding=me.Padding.all(20),
        margin=me.Margin.all(20, 0, 0, 0),
        border_radius=10,
        width="100%",
        max_width="800px",
    )):
        me.text("Generated Clinical Profile", type="headline-5")
        me.text(f"Character: {profile_dict.get('character_name', 'N/A')}", type="subtitle-1")
        me.text(f"Profile Date: {profile_dict.get('profile_date', 'N/A')}", type="body-2")

        me.text("Overall Assessment:", type="headline-6", style=me.Style(margin=me.Margin.all(15, 0, 0, 0)))
        summary = profile_dict.get('overall_assessment_summary', 'No summary provided.')
        me.text(summary)

        # Display Holland Code Assessment
        holland_assessment = profile_dict.get('holland_code_assessment')
        if holland_assessment:
            me.text("Holland Code (RIASEC) Assessment:", type="headline-6", style=me.Style(margin=me.Margin.all(15, 0, 0, 0)))
            me.text(f"Top Themes: {', '.join(holland_assessment.get('top_themes', []))}", type="subtitle-2")
            me.text(f"Summary: {holland_assessment.get('summary', 'No summary provided.')}")
            with me.box(style=me.Style(margin=me.Margin.all(10, 0, 0, 15))):
                for score in holland_assessment.get('riasec_scores', []):
                    me.text(f"- {score.get('theme')}: {score.get('score')}/10", style=me.Style(font_weight="bold"))
                    me.text(score.get('description'))


        diagnoses = profile_dict.get('diagnoses', [])
        if not diagnoses:
            me.text("No formal diagnoses were assigned.", style=me.Style(margin=me.Margin.all(15, 0, 0, 0)))
        else:
            me.text("Diagnostic Impressions:", type="headline-6", style=me.Style(margin=me.Margin.all(15, 0, 0, 0)))
            for dx in diagnoses:
                with me.box(style=me.Style(margin=me.Margin.all(10, 0, 0, 15))):
                    me.text(f"{dx.get('disorder_name', 'N/A')} ({dx.get('dsm_code', 'N/A')})", type="subtitle-2")
                    me.text(f"Category: {dx.get('dsm_category', 'N/A')}", type="body-2")

                    specifiers = dx.get('specifiers', [])
                    if specifiers:
                        me.text("Specifiers:", style=me.Style(font_weight="bold"))
                        for s in specifiers:
                            me.text(f"- {s.get('specifier_type')}: {s.get('value')}")

                    me.text("Criteria Met (Justification):", style=me.Style(font_weight="bold", margin=me.Margin.all(5, 0, 0, 0)))
                    criteria = dx.get('criteria_met', [])
                    if criteria:
                        for c in criteria:
                            me.text(f"- {c}")
                    else:
                        me.text("- None listed.")

                    me.text("Functional Impairment:", style=me.Style(font_weight="bold", margin=me.Margin.all(5, 0, 0, 0)))
                    impairment = dx.get('functional_impairment', 'Not specified.')
                    me.text(impairment)

                    note = dx.get('diagnostic_note')
                    if note:
                        me.text("Notes:", style=me.Style(font_weight="bold", margin=me.Margin.all(5, 0, 0, 0)))
                        me.text(note)
