# ML model pipeline

This is a simple ML model pipeline that uses the following libraries:

### Project Setup:
1. Download the repository
2. Run docker-compose build
3. Run docker-compose up
4. Open a browser and go to http://localhost:8000

### Usage:
Open a browser and go to http://localhost:8000/docs
for the API documentation

When deploying in production, make sure to change the environment variable in the docker-compose file to production

### Database:
Uses Supabase as the database for SQL and S3 storage
Models and training-data are stored in the S3 buckets

