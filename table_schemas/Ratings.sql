CREATE TABLE Ratings(
	state VARCHAR(255),
	license_plate VARCHAR(255),
	cleanliness FLOAT,
	reliability FLOAT,
	cosmetics FLOAT,
	overall_rating FLOAT,
	number_of_reviews INT,
	FOREIGN KEY (state, license_plate) REFERENCES Cars(state, license_plate) ON DELETE CASCADE,
	PRIMARY KEY (state, license_plate)
);