CREATE TABLE IF NOT EXISTS initiatives
(
	channel_id		 	TEXT,
	round_number		INTEGER DEFAULT 0,
	cur_initiative 	INTEGER DEFAULT -1,
	label						TEXT DEFAULT NULL,
	verbose					INTEGER DEFAULT 1,
	start_time			DATETIME,
	PRIMARY KEY (channel_id)
);

CREATE TABLE IF NOT EXISTS characters
(
	channel_id	  	TEXT,
	mention					TEXT,
	name				 		TEXT DEFAULT NULL,
	num_dice				INTEGER,
	num_ego					INTEGER DEFAULT 0,
	num_successes		INTEGER,
	num_triggers 		INTEGER,
	num_ones				INTEGER,
	PRIMARY KEY (channel_id, mention, name),
	FOREIGN KEY (channel_id) REFERENCES initiatives(channel_id)
);

CREATE TABLE IF NOT EXISTS initiative_values
(
	channel_id			TEXT,
	value						INTEGER,
	PRIMARY KEY (channel_id),
	FOREIGN KEY (channel_id) REFERENCES initiatives(channel_id)
);
