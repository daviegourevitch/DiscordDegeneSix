CREATE TABLE IF NOT EXISTS initiatives
(
	channel_id		 	TEXT,
	round_number		INTEGER DEFAULT 0,
	cur_initiative 	INTEGER DEFAULT -1,
	label						TEXT DEFAULT NULL,
	verbose					INTEGER DEFAULT 1,
	PRIMARY KEY (channel_id)
);

CREATE TABLE IF NOT EXISTS characters
(
	channel_id	  	TEXT,
	mention					TEXT,
	name				 		TEXT DEFAULT NULL,
	num_triggers 		INTEGER,
	num_successes		INTEGER,
	num_dice				INTEGER,
	num_ego					INTEGER DEFAULT 0,
	PRIMARY KEY (channel_id, mention),
	FOREIGN KEY (channel_id) REFERENCES initiatives(initiative_id)
);
