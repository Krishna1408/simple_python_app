#  GCP - Test Python API's

##Overview:

The given python script does below tasks:
1. Create a Instance
2. Delete a Instance
3. Get Healtcheck of created instance
4. Get available Methods

User can update the python file to get more flexibility with instance creation.

## Prerequisites:

1. You should have python version 3 installed.
2. Python modules are "google-api-python-client" And "flask" `Use: pip3 install `
```yaml
   In Amazon Linux below commands can be used:
   pip3 install --upgrade google-api-python-client
   pip3 install flask
```

3. Create a Project in Google Cloud

4. Get API keys from google cloud dashboard:
 `APIs & Services >  Credentials > Create Credentials > Service Account Keys > Save the json file`

5. Export the downloaded json key file: `export GOOGLE_APPLICATION_CREDENTIALS=/path_to_keys/key.json`

6. Clone/download this project and update the *input.txt* file:
```yaml
   project=your_project_id
   zone=zone_for_gce
   instance_name=instance_name_of_your_choice
```

```yaml
   Example:
   project=analog-bay-13434324
   zone=us-east1-c
   instance_name=Test-instance
```

## Running the code:
1. Run the application file: `python3 simple_python_app.py`
2. To get the available methods: `http://localhost:5000/`
3. To create the instance: `curl -H "Content-Type: application/json" -X POST -d '{"username":"Your_User", "password": "Your_passowrd"}' http://localhost:5000/v1/instances/create`
4. To get healthcheck: `curl http://localhost:5000/healthcheck`
5. To delete the instance: `curl -X DELETE  http://localhost:5000/v1/delete_instance`

User can also use postman instead of curl commands.

###Additional info:
1. The python application runs on localhost at port 5000. User can also use IP of localhost.
2. /healthcheck gives a 200 OK response and no other output.
3. If Instance is down /healthcheck will give you error 404
4. To login to the instance use the username and password provided during the create instance call.



