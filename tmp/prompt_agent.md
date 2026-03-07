You are an experienced Python developer with knowledge of how multi-process Python works.

# <u>Architecture</u>
Creation of an agent that runs and can deliver text markdown files a location based on a subscription model.
- Files are stored and retrieved by an agent in a Postgres SQL database table
- File status is stored and persisted in the prm_subscription_file table

<u>Components</u>

**AgentAPI**: It will exist as a FastAPI API service running on port 5333 and is responsible for getting and putting subscription file
content into and out of the database table.  The AgentAPI will interact with the tables defined by the table structured 
described by these services:

    http://localhost:8000/tables/prm_subscription_file/structure
    http://localhost:8000/tables/prm_subscriber/structure

The **AgentAPI** fill have the following capabilities:
- Get subscriber - the details about a project subscriber
- Put subscriber - when registering a project as a subscriber, it enters the project, area and status that is desired
- Get by subscriber id - get details about a subscriber
- Get files file for a subscriber id - get the list of files for the subscriber id
- Upload file - Upload a flie along with details regarding its: project, area, and status
- Update the status of a file file id

**AgentDaemon**: A long running program that is a a Python script installed on a server that checks every 60 seconds (configurable) 
if files are ready to be delivered to subscribers to their configured destination location.  It will then based on the status of
the delivered file execute an action on the recieved file.

Actions that the AgenDaemon could involve the execution of scripts:
    - pi_run.sh  <model>  <filename> : execute an LLM CLI on the subscribed file that has been delivered
    - action.sh <command> <filename> : some action which will be defined later in the future, most likely used for cleanup 

Once the AgentDaemon has delivered the file it should update the prm_subscription_file status for the file using the API to do the 
following state transitions of the status field:
PENDING->RUNNING->{COMPLETED or ERROR}


# <u>Requirements</u>

These are the specific requirements for the software requested.   It will cover a project registration component,
a daemon component, and a publisher component

<u>Registration of project with AgentDaemon</u>

The user will register itself with the AgentDaemon as a consumer and indicate what files they are interested in based on a heirarchy:
    - project: the name of the project that the user is interested in
    - area: the area of interest the project is concerned with.  Samples are front-end, back-end, testing, design etc.
    - status: the status of the file, the status could be: PENDING,ERRORED.. etc.   The default is PENDING
    - timestamp: the client might only be interested in subscribed files starting from a particular update_ts timestamp

The AgenDaemon will use the AgentAPI service to register the project user with their desired subscription.

The AgentDaemon should only download files using the AgentAPI for files that meet project, area, and status criteria which
is maintained by the API (persisted in the prm_subscriber table).

The AgentDaemon upon registration will by default use the current directory where the AgentDaemon is called in registration
mode as the operation directory for subscriptoins.   The AgentDaemon will make a call to the AgentAPI server during registration
to store and track where the destinaton folder is located.

The AgentDaemon will also create a .agent folder in the project folder where it will download and execvute instructions files from.

<u>AgentDaemon Subscriber</u>

The AgentDaemon process will be a long running daemon process which will periodically check for the various projects that have
been registered on the local system for records that match the project subscription in terms of : project, area and status

Usually the 'status' field that it will be subscribing for is: PENDING however in the future we might also have it try to 
get and process subscriptions that might have been in ERROR status.

Upon matching the subscription criteria for a project it will:
- Call the AgentAPI to download the instruction file and write the instruction file into the .agent folder.
    Store the file in the .agent folder and append the datestamp to it, for example:   hello_cmd.md.20260306_120432
- Call following command on resultant file:
    pi -p --no-session --tools "read,bash,edit,write"  ./agent/<downloaded_file>
- Upon successfull completion of the execution of the file the AgentDaemon will update the subscription status of the file
using the AgentAPI to one of:
    RUNNING - Once the execution of the file has started
    COMPLETED - Once the processing has succefully completed
    ERROR - If there is an error processing the file

The AgentDaemon must be able to run multiple file executions in parallel in seperate processes. 

<u>Publisher - Upload of Files</u>
The AgentDaemon will also call the AgentAPI in order to publish files.  When publishing files the AgentDaemon needs
to provide the following details:
- file_name: name of the file
- project: intended project
- area: intended area
- status: the status of the file, by default it should be pending
- description: any available description or meta-information about the file

Upon receipt of the file the AgentAPI should check the prm_subscriber table to see which files matches the subscription
fields for the uploaded file and insert into that table with a PENDING status.


<u>Implementation Instructions</u>

- Create the AgentAPI FastAPI service
- Create the AgentDaemon python script which runs in daemon mode or in registration mode
