CREATE TABLE Availability(
	state VARCHAR(255),
	license_plate VARCHAR(255),
	start_date_time DATETIME,
	end_date_time DATETIME,
	FOREIGN KEY (state, license_plate) REFERENCES Cars(state, license_plate) ON DELETE CASCADE
);
