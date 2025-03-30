-- Create enum types
CREATE TYPE employment_type AS ENUM ('full_time', 'part_time', 'unemployed');
CREATE TYPE marital_status AS ENUM ('single', 'married', 'divorced');
CREATE TYPE device_type AS ENUM ('desktop', 'mobile', 'tablet');
CREATE TYPE model_status AS ENUM ('training', 'deployed', 'failed', 'inactive', 'pending');

-- Create Applicant table
CREATE TABLE applicants (
    user_ID UUID PRIMARY KEY,
    age INT NOT NULL,
    income FLOAT NOT NULL,
    employment_type employment_type NOT NULL,
    marital_status marital_status NOT NULL,
    time_spent_on_platform FLOAT NOT NULL,
    number_of_sessions INT NOT NULL,
    fields_filled_percentage FLOAT NOT NULL,
    previous_year_filing BOOLEAN NOT NULL,
    device_type device_type NOT NULL,
    referral_source TEXT NOT NULL,
    completed_filing BOOLEAN NOT NULL
);

CREATE TABLE training_data(
    model_training_data_ID UUID PRIMARY KEY,
    model_training_data_URL TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_status BOOLEAN NOT NULL
);

-- Create MLModel table
CREATE TABLE ml_models (
    model_ID UUID PRIMARY KEY,
    model_URL TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_filename TEXT NOT NULL,
    accuracy FLOAT NOT NULL,
    model_precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    modified_at TIMESTAMP WITH TIME ZONE NOT NULL,
    model_state model_status NOT NULL,
    model_training_data_ID UUID NOT NULL,
    model_version TEXT NOT NULL,
    trained_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create Scenario table
CREATE TABLE scenarios (
    scenario_ID UUID PRIMARY KEY,
    scenario_name TEXT NOT NULL,
    description TEXT NOT NULL,
    current_model_ID UUID REFERENCES ml_models(model_ID)
);


-- Create PredictionResponse table
CREATE TABLE prediction_responses (
    prediction_ID UUID PRIMARY KEY,
    result BOOLEAN NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    applicant_ID UUID REFERENCES applicants(user_ID)
);

-- Create junction table for Scenario Model join
CREATE TABLE scenario_models(
    scenario_ID UUID REFERENCES scenarios(scenario_ID),
    model_ID UUID REFERENCES ml_models(model_ID),
    is_active BOLEAN DEFAULT FALSE,
    activated_on TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (scenario_ID, model_id)
);
