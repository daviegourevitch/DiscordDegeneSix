CREATE TABLE IF NOT EXISTS initiatives
(
	initiative_id 	INTEGER,
	cur_initiative 	INTEGER,
	initiative_name TEXT,
	PRIMARY KEY (initiative_id)
);

CREATE TABLE IF NOT EXISTS player
(
	initiative_id  	INTEGER,
	player_name 		TEXT,
	num_triggers 		INTEGER,
	num_successes		INTEGER,
	num_ego					INTEGER,
	PRIMARY KEY (initiative_id, player_name),
	FOREIGN KEY (initiative_id) REFERENCES initiatives(initiative_id)
);
