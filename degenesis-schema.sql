CREATE TABLE initiatives
(
	channel_id		 	TEXT,
	round_number		INTEGER,
	cur_initiative 	INTEGER,
	initiative_name TEXT,
	PRIMARY KEY (channel_id)
);

CREATE TABLE player
(
	channel_id	  	INTEGER,
	discord_id			TEXT,
	player_name 		TEXT,
	num_triggers 		INTEGER,
	num_successes		INTEGER,
	num_dice				INTEGER,
	num_ego					INTEGER,
	PRIMARY KEY (initiative_id, discord_id),
	FOREIGN KEY (initiative_id) REFERENCES initiatives(initiative_id)
);
