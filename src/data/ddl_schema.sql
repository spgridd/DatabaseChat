CREATE TABLE leagues(
    league_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(45), -- League name e.g. Premier League, La Liga etc.
    country VARCHAR(45), -- Origin country of the league e.g. England, Spain etc.
    website VARCHAR(45) -- Official league website e.g. premierleague.com, laliga.com etc.
);

CREATE TABLE teams (
    team_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    league_id INT,
    name VARCHAR(45), -- Team name e.g. FC Barcelona, Real Madrid, Manchester United etc.
    place INT, -- Curent place in the table e.g. 1, 2, 15 etc.
    FOREIGN KEY (league_id) REFERENCES leagues(league_id)
);

CREATE TABLE players (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    team_id INT,
    name VARCHAR(45), -- Player name e.g. Lionel, Cristiano, Marc etc.
    surname VARCHAR(45), -- Player surname e.g. Messi, Ronaldo, Casado etc.
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);