CREATE TABLE Car(
	state VARCHAR(255) ,
	license_plate VARCHAR(255) ,
	odometer INT,
	mpg INT,
	make VARCHAR(255) ,
	model VARCHAR(255),
	year YEAR,
	owner_id INT,
	FOREIGN KEY (owner_id) REFERENCES Users (user_id) ON DELETE CASCADE,
	PRIMARY KEY( state,license_plate)
);
