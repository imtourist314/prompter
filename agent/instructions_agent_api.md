You are an experienced Python developer with knowledge of how multi-process Python works.

<u>Architecture</u>

Creation of an agent that runs and can deliver text markdown files a location based on a subscription model.
- Files are stored and retrieved by an agent in a Postgres SQL database table
- The agent_daemon will register a project and add it as a subscriber by also recording in the prm_subscriber table
the 'project', 'area', and 'component' criteria for which it wishes to subscribe for files
- File contents and status is stored and persisted in the prm_subscription_file table

<u>Components</u>

**AgentAPI**: It will exist as a FastAPI API service running on port 5333 and is responsible for getting and putting subscription file
content into and out of the database table.  The AgentAPI will interact with the tables defined by the table structured 
described by these services:

    http://ls1.lambda-tech.ca:8000/tables/prm_subscriber/structure
    http://ls1.lambda-tech.ca:8000/tables/prm_subscription_file/structure

The **AgentAPI** fill have the following capabilities:
- Get subscriber or list of subscribers - the details about a project subscriber
- Put or create a new subscriber - when registering a project as a subscriber, it enters the project, area, component, and status that is desired
- Get by subscriber id - get details about a subscriber
- Get files file for a subscriber id - get the list of files for the subscriber id
- Get all files - get the full list of files
- Upload file - Upload a flie along with details regarding its: project, area, component, and status
- Update the status of a subscription file file id
- Get unique list of projects by performing a unique on the prm_subscriber table for projects
- Get unique list of project areas by performing a unique on the prm_subscriber table for areas
- Get unique list of project components by performing a unique on the prm_subscriber table for components


The connection parameters to the PostgresSQl database is:
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/corp

