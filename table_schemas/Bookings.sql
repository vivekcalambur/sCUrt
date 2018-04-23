CREATE TABLE Bookings(
	renter_id INT,
	state VARCHAR(255),
	license_plate VARCHAR(255),
	start_date_time DATETIME,
	end_date_time DATETIME,
	FOREIGN KEY (renter_id) REFERENCES Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY Bookings(state, license_plate) REFERENCES Cars(state, license_plate) ON DELETE CASCADE
);