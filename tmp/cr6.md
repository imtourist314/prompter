Modify the agent-daemon with the following changes:
- Properly log that the name of the flie that is being processed by the LLM CLI
- The daemon should create a .agent folder in the directory for each project where it puts the downloaded flies form the API
- The downloaded file should have a timestamp appended to the name when it is put in the .agent directory, for example hello_cmd.md.20260307_040303
- The daemon should only update the subscribed file as being completed only after the LLM CLI has completed its processing of the file
