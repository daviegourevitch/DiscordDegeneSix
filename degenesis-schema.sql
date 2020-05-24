CREATE TABLE IF NOT EXISTS initiatives
(
	channel_id		 	TEXT,
	round_number		INTEGER,
	cur_initiative 	INTEGER,
	initiative_name TEXT,
	PRIMARY KEY (channel_id)
);

CREATE TABLE IF NOT EXISTS player
(
	channel_id	  	INTEGER,
	discord_id			TEXT,
	player_name 		TEXT,
	num_triggers 		INTEGER,
	num_successes		INTEGER,
	num_dice				INTEGER,
	num_ego					INTEGER,
	PRIMARY KEY (channel_id, discord_id),
	FOREIGN KEY (channel_id) REFERENCES initiatives(initiative_id)
);
