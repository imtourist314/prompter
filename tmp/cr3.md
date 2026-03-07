In the AgentAPi get rid of the prm_subscriber_state.  It is not needed since prm_subscription_file will be able
to record and track:
- the file and file contents
- the intended project and area
- the status of the file as its processing

Use the database connection parameters in the file .env in order to connect to the database to look at the tables.
