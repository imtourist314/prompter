
# High Level Design

Create a web UI client called "Prompter" using the Vue framework which is able to use the AgentAPI service to:
- select a project, area, and component
- enter into a 25 line text box instructions
- submit the contents of the textbox and publish using the AgentAPI /files POST API call
- view the status of published files, those that are PENDING, RUNNING, ERRRO etc.

Use the AgentAPI API that is published here:
http://ls1.lambda-tech.ca:5333/docs#/

# Requirements #

<u>Project and Area Selection</u>
- Project and area should appear as separate selectable drop-downs on the top right of the screen
- The main pane of the screen should consist of a tabbed interface with one tab per component
- The content of the main pane will be a text box on the left hand side where the user can enter
   raw text and on the right hand size will be a markdown preview page which will render as the user
   enters text.
    - A 'Preview'  checkbox item on the top right will either show or hide the markdown preview
- Above the main pane will be a 'Submit' and 'Cancel' button:
    - Submit: will submit and publish the conents of the text box
    - Cancel: will reload or revert the contents of the text box
- Below the main pane will another pane which will include a table of subscription files for the
  current project and area

Create this web UI client and put the UI in a directory in this project at ./client
