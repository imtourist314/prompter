# Adjust Markdown text box height and preview pane

## Summary
- Reduce the Markdown editor's minimum height from 40 to 20 rows so prompts are easier to edit on smaller screens.
- Keep the live preview pane in lockstep with the textarea height so the split view stays balanced.
- Regenerate the Vite production bundle so the published UI picks up the new sizing defaults.

## Changes
- `client/src/components/MarkdownTextBox.vue`: lower the default `rows` attribute and the CSS `min-height` for both the textarea and preview pane.
- `client/dist/index.html`: reference the freshly-built hashed JS and CSS artifacts.
- `client/dist/assets/index-*.{js,css}`: updated Vite build output that contains only the sizing tweaks above.

## Testing
- `cd client && npm run build`
