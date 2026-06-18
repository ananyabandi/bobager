# bobager

A static frontend for the Bobager AI chatbot.

## Features

- IBM Bob-inspired chatbot layout
- Blue / purple gradient theme matching the icon
- Included robot icon as `logo.svg`
- Local chat UI ready for backend integration

## Files

- `index.html` — main chatbot UI
- `styles.css` — theme and layout styles
- `app.js` — chat behavior and simulated responses
- `logo.svg` — custom robot icon asset

## Getting started

Open `index.html` in your browser, or serve the folder with a local static server.

Example using Python:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Integration

To connect a real AI backend, update `app.js` and replace the `getBotResponse` logic with your API call.
