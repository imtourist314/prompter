# Summary
- Extend the FastAPI-backed AgentAPI: promote `component` to a required column on subscribers/files via lightweight boot-time migrations, add supporting schema/CRUD changes, and expose project/area/component metadata plus richer file filters in the public endpoints.
- Modernize the AgentDaemon CLI/client so every command understands the new component dimension, improves status normalization, surfaces the component through list output/action context, and adds conveniences like inline content publishing and stricter themeable config persistence.
- Replace the deprecated Express/Vue bundle with a redesigned Vite + Vue 3 Prompter UI that talks directly to AgentAPI (new fetch helper, theme toggle, project/area selectors, component tabs, dual-pane markdown editor with preview toggle, status table modal viewer, and dist assets), alongside fresh design docs and dependency updates.

## Testing
- `npm --prefix client run build`
