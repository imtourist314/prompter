# LLM enhanced changes 20260308_070501

## Summary
- Automated PR generated from local changes.

## Changes
```
 .job_listener/back-end/completed_instructions.md  |   3 -
 .job_listener/back-end/instructions.md            |   2 -
 .job_listener/front-end/completed_instructions.md |   1 -
 .job_listener/front-end/instructions.md           |   2 -
 README.md                                         |  14 +
 agent/.prompt_agent.md.swp                        | Bin 16384 -> 0 bytes
 agent/README.md                                   |  30 +-
 agent/agent_api/crud.py                           |  51 +-
 agent/agent_api/database.py                       |   2 +
 agent/agent_api/main.py                           |  34 +-
 agent/agent_api/migrations.py                     |  55 ++
 agent/agent_api/models.py                         |  17 +-
 agent/agent_api/schemas.py                        |   5 +-
 agent/agent_daemon/client.py                      |  27 +
 agent/agent_daemon/daemon.py                      |  28 +-
 agent/instructions_agent_api.md                   |  35 +
 client/dist/assets/index-BHLjjpL1.css             |   1 -
 client/dist/assets/index-BL7DFp6Z.css             |   1 +
 client/dist/assets/index-DjxQA8lV.js              |  63 ++
 client/dist/assets/index-DnQxD7OY.js              |  62 --
 client/dist/index.html                            |   4 +-
 client/package-lock.json                          | 425 ++++------
 client/package.json                               |   9 +-
 client/src/App.vue                                | 991 ++++++++++++++--------
 client/src/api.js                                 |  88 --
 client/src/api/agentApi.js                        | 103 +++
 client/src/assets/main.css                        |  66 ++
 client/src/components/ComponentTabs.vue           | 117 +++
 client/src/components/InstructionEditor.vue       | 184 ++++
 client/src/components/MarkdownTextBox.vue         | 129 ---
 client/src/components/ProjectAreaSelector.vue     |  97 +++
 client/src/components/StatusTable.vue             | 196 +++++
 client/src/components/TabEditor.vue               | 369 --------
 client/src/main.js                                |   7 +-
 client/vite.config.js                             |  37 +-
 client_ui.md                                      |  28 +
 generated_pr.md                                   |  14 +-
 instructions.md                                   |   3 -
 package.json                                      |   7 +-
 server/index.js                                   | 433 ----------
 tmp/hello2.md                                     |   5 +
 tmp/switch_ui_back_end.md                         |   2 +
 tmp/switch_ui_back_end_2.md                       |   5 +
 43 files changed, 1998 insertions(+), 1754 deletions(-)
```

## Files changed
```
.job_listener/back-end/completed_instructions.md
.job_listener/back-end/instructions.md
.job_listener/front-end/completed_instructions.md
.job_listener/front-end/instructions.md
README.md
agent/.prompt_agent.md.swp
agent/README.md
agent/agent_api/crud.py
agent/agent_api/database.py
agent/agent_api/main.py
agent/agent_api/migrations.py
agent/agent_api/models.py
agent/agent_api/schemas.py
agent/agent_daemon/client.py
agent/agent_daemon/daemon.py
agent/instructions_agent_api.md
client/dist/assets/index-BHLjjpL1.css
client/dist/assets/index-BL7DFp6Z.css
client/dist/assets/index-DjxQA8lV.js
client/dist/assets/index-DnQxD7OY.js
client/dist/index.html
client/package-lock.json
client/package.json
client/src/App.vue
client/src/api.js
client/src/api/agentApi.js
client/src/assets/main.css
client/src/components/ComponentTabs.vue
client/src/components/InstructionEditor.vue
client/src/components/MarkdownTextBox.vue
client/src/components/ProjectAreaSelector.vue
client/src/components/StatusTable.vue
client/src/components/TabEditor.vue
client/src/main.js
client/vite.config.js
client_ui.md
generated_pr.md
instructions.md
package.json
server/index.js
tmp/hello2.md
tmp/switch_ui_back_end.md
tmp/switch_ui_back_end_2.md
```

## Testing
- Not specified.
