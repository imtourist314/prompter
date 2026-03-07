Using FastAPI database discovery service: http://ls1.lambda-tech.ca:8000/docs, this service has an API call to get the list of tables as well as the structure of each table.

Perform the following changes for the table prm_instructions which already exists in the database create an API that will do the following:
- Insert an entry into this database table.  New inserts have a status=PENDING
- Update an entry in this database table
- Query and retrieve entries from this database table