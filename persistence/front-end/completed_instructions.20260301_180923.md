You are an expert front-end and back-end developers.  You are creating an application called 'Prompter'
which will assist with giving other LLMs instructions on code generation, and testing.

# High Level Architecture
- Front end written using the Vue framework
- Front end is a multi-tab UI
- Persistence of data that the user enters stored locally in files with one directory per tab
    - Each tab will display and persist two textboxes that are markdown aware
    - Data that is entered into the text boxes will be persisted in a directory for that tab
    - Each tab will include a markdown-aware textbox entry for current instruction text, and another markdown-aware textbox for instructions
     which have already been processed
    - One tab tracks instructions for 'front-end' development
    - Second tab tracks instructions for 'back-end' development
    - Third tab tracks instructions for 'testing' development
- An API that is available to pull the current instructions and also for already-processed instructions

# Setup
- Ensure that the correct NPM packages to support Vue and vite are installed

# Front end
Develop a Vue web application that has multiple tabs:
    - 'Front-end' development
    - 'Back-end' development
    - 'Testing' development
Each tab will consist of two textboxes in which markdown text can be entered
    - Top textbox will consist of current instructions
    - Bottom textbox will consist of one or more instruction files which have already been processed
    - A submit or cancel button.  If cancel is pressed any changes in the textboxes are wiped out and re-read from the
    the filesystem
    - The submit button will write the contents of textbox to a folder structure
        - ./persistence/front-end/instructions.md for current instructions and ./persistence/front-end/completed_instructions.md for completed instructions
        - ./persistence/back-end/instructions.md for current instructions and ./persistence/back-end/completed_instructions.md for completed instructions
        - ./persistence/testing/instructions.md for current instructions and ./persistence/testing/completed_instructions.md for completed instructions
    - Make the textboxes at least 40 lines long
Create a proxy configuration to allow CORS access to the webservice.
Create a toggle switch at the top to allow switching between light mode and dark mode.

# API
- Create an API endpoint that clients can use to access the files from the folder structure.
- The endpoints should of form:  http://<servername>:<port>/api/instructions/<front-end|back-end|testing>/instructions.md

# Listener
- Create a python script which will use the API in order to download the instructions.md and the completed_instructions.md file
- The python script should indicate as an argument if it is for front-end, back-end or for testing
- The listener should check every 60 seconds if there is any new set of instructions to act on
- It should compare the new instructions.md file and the completed_instructions.md file to see if they are new by comparing them to the existing file
- Assume that the requests python library is already installed

# Github instructions
- Create a shell script called scripts/github_publish.sh which will
    - initialize the current 'Prompter' project for checking into github
    - create instructions for the initial push of the project into github

