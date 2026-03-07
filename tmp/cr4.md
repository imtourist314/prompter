For the AgentDaemon when in publish mode only one of --file-name or --content is required, but not both.
--file-name : is the filename which is sent to the AgentAPI where its recorded and its contents are loaded into the prm_subscription_file table
--content : can be text which is directly loaded by the AgentAPI into the contents field in the prm_subscription_file table

Also, when for the AgentAPI if there are no subscription files just return an empty response in instead of the current "404 Not found" error message.
