CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	creation_date DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	date_of_birth DATE, 
	goal VARCHAR(100), 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);
CREATE TABLE lifts (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	targeted_area VARCHAR(30) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE plans (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	plan_name VARCHAR(100) NOT NULL, 
	plan_type VARCHAR(50), 
	plan_duration VARCHAR(50), 
	creation_date DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE plan_lifts (
	id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	lift_id INTEGER NOT NULL, 
	sets INTEGER, 
	reps INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(plan_id) REFERENCES plans (id), 
	FOREIGN KEY(lift_id) REFERENCES lifts (id)
);
CREATE TABLE lift_performances (
	id INTEGER NOT NULL, 
	plan_lift_id INTEGER NOT NULL, 
	lift_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	date DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	reps_performed INTEGER NOT NULL, 
	weight_performed FLOAT NOT NULL, 
	reps_in_reserve INTEGER NOT NULL, 
	recommended_weight FLOAT, 
	additional_notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(plan_lift_id) REFERENCES plan_lifts (id), 
	FOREIGN KEY(lift_id) REFERENCES lifts (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
