
### Genera API endpoints

The system uses /v1/scenarios for multiple scenarios in the future where different ML model scenarios could be used

#### API design
- GET /v1/scenarios
	- endpoint to get a list of available scenarios with scenario name, scenario_ID and scenario description
- GET /v1/scenarios/\$scenario_ID
	- return the current scenario name, scenario_ID, description, currently loaded model
- GET /v1/ scenarios/\$scenario_ID/models
	- List available models for the selected scenario
- POST /v1/scenarios/\$scenario_ID/predict
	- run prediction using the currently loaded model
- POST /v1/scenarios/\$scenario_ID/train/training_data
- POST /v1/scenarios/\$scenario_ID/train/\$data_ID
- POST /v1/scenarios/\$scenario_ID/models/\$model_ID/activate
- DELETE /v1/scenarios/\$scenario_ID/models/\$model_ID

Data models
model:
model_id
model_name
model_filename
model_URI
creation_time
statistics{
accuracy,
....
}
creation_user
status: {time: , model_status}