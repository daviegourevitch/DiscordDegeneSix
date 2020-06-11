CREATE TABLE IF NOT EXISTS initiatives
(
	channel_id		 	TEXT,
	round_number		INTEGER DEFAULT 1,
	cur_initiative 	INTEGER,
	label						TEXT,
	is_closed				INTEGER DEFAULT 0,
	PRIMARY KEY (channel_id)
);

CREATE TABLE IF NOT EXISTS characters
(
	channel_id	  	TEXT,
	discord_id			TEXT,
	name				 		TEXT,
	num_triggers 		INTEGER,
	num_successes		INTEGER,
	num_dice				INTEGER,
	num_ego					INTEGER,
	PRIMARY KEY (channel_id, discord_id),
	FOREIGN KEY (channel_id) REFERENCES initiatives(initiative_id)
);
