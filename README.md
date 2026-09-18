# SARA

> hello there 👋
>
> What I have here is SARA, a small, homemade AI overlay for Windows.

SARA is an experimental Windows utility that captures a screenshot when invoked with a keyboard shortcut, sends it to the Gemini API together with a prompt, and displays the response in a temporary floating overlay.

## How It Works
SARA follows a simple workflow:

1. Press the configured keyboard shortcut.
2. SARA captures the current screen.
3. The screenshot and prompt are sent to Gemini.
4. Gemini processes the request and returns a response.
5. SARA displays the response in a lightweight overlay.
6. The overlay automatically dismisses after approximately 8 seconds

The overlay is designed to minimize disruption to the currently active Windows application.

## Features

- Gemini API support
- Screenshot-based AI interaction
- Keyboard shortcut activation
- Lightweight floating overlay
- Minimal interaction with Windows focus
- Automatic overlay dismissal
- Dynamic sizing
- Windows support

## Setup

First, install the required packages:

    pip install google-genai pillow mss keyboard

After that finishes, close the terminal and open `sara.py` using a text editor or Visual Studio Code.

Find the API key section and replace it with your own Google Gemini API key.

Then run:

    python sara.py

That's basically it.


## Requirements

- Windows
- Python 3.x
- A Google Gemini API key
- Internet connection

## Gemini API & Privacy
SARA uses the Gemini API to process screenshots and prompts.

When SARA is invoked, the captured screen content is sent to Google through the Gemini API for processing.

Do not use SARA with sensitive information unless you understand and are comfortable with how that information is handled by the services involved.

Please keep your API key private and never commit it to GitHub.

You are responsible for your own API usage and any associated charges.

Please make sure your use of the Gemini API complies with Google's current terms, quotas, and policies.

## Intended Use
SARA is a general-purpose AI and productivity experiment.

Possible uses include:

- Simplifying and breaking topics down
- Research or find topic on screen
- Finding errors or solutions
- General productivity

Always follow the rules and policies of the environment or service in which you use SARA.

## Current Status

SARA is still experimental and has not been thoroughly tested.

| Feature | Status |
|---|---|
| Static overlay | ✅ |
| Gemini API | ✅ |
| Keyboard input | ✅ |
| Windows | ✅ |
| Linux | ❌ |
| macOS | ❌ |
| Perfectly bug-free | ❌ |

## Disclaimer

SARA is experimental software.

> Use it at your own risk.

I am not responsible for API charges, account issues, data loss, software crashes, service interruptions, or violations of third-party terms and policies.

Please check the terms and policies of any services you use with SARA.

## Version

**First GitHub version:** `SARA 1.5`

**Current version:** `SARA 1.5`