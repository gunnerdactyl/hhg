# Happy Hunting Grounds

https://happy-hunting-grounds.streamlit.app/

Happy Hunting Grounds (HHG) is a game where players test their knowledge of Premier League away goals.

The game format was created by [Adam Hurrey](https://twitter.com/footballcliches) for the [Football Cliches podcast](https://linktr.ee/footballcliches).

This online version of HHG was created by Jacob. I go by [@gunnerdactyl](https://twitter.com/gunnerdactyl) on Twitter, for my sins.

If you find any bugs, bad data, or weird behavior in the app, email gunnerdactyl [with a gmail suffix].

## How to play

The two players take turns. During their turn, the player selects a difficulty level with the slider (1=easiest, 10=hardest). This difficulty level also represents the number of points that the player can earn for a fully-correct answer.

Players are presented with a "Team @ Venue" hunting ground prompt and they must name a player who scored for the given team at that particular away ground and the season during which they did it. The game covers the Premier League seasons from 1992/1993 through 2022/2023. (2023/2024 goals are not included!)

## Scoring

If the player correctly names a goalscorer for the given team at the given venue, they receive points equal to half the difficulty level. If they also get the season correct, they receive the other half of the points. No points are awarded for having the correct season but an incorrect name.

### Fuzzy name matching

Goal scorer responses are fuzzy-matched with the correct answers, so perfect spelling is not required, but the closer you are, the better.

For best results, use both first and last names. This is especially true for players whose names include accented characters or other characters not part of the standard English alphabet. For example, if you want to guess `İlkay Gündoğan`, entering `gundogan` will _not_ meet the threshold for a correct answer, but `ilkay gundogan` will be a successful match.

## Difficulty levels

The difficulty level of a hunting ground is set using a combination of team performance and the number of away goals scored by a team at a particular venue. This reflects two guiding assumptions about difficulty:

1. Goals in games between the most successful teams are easier to remember.
2. Matchups where more away goals have been scored are easier to remember, though this factor is not as powerful as the first.

For each away goal scored during the Premier League era, the away _and_ home teams received a score based on their final league position during that particular season. Then, those scores for the two teams were added together and called the `team performance` for that goal.

Next, for each away team/home team/stadium combination, the `average team performance` of all the away goals scored was calculated.

Also for each combination, the total number of away goals was divided by two and called `goal volume`. Raw difficulty points for the matchup were calculated as `average team performance + goal volume`.

Armed with raw difficulty scores for all the away/home/stadium combinations, the Jenks natural breaks algorithm was applied to create ten difficulty thresholds.

Here is an example hunting ground for each difficulty level.

| Difficulty | Example hunting ground|
| :--------: | :---------- |
| 1 |  Tottenham Hotspur @ Emirates Stadium |
| 2 |  Newcastle United @ Goodison Park |
| 3 |  Southampton @ Anfield |
| 4 |  Stoke City @ Old Trafford |
| 5 |  Birmingham City @ Emirates Stadium |
| 6 |  Bournemouth @ Tottenham Hotspur Stadium |
| 7 |  Crystal Palace @ Stadium of Light |
| 8 |  Watford @ Cardiff City Stadium |
| 9 |  Brentford @ Turf Moor |
| 10 |  Ipswich Town @ Selhurst Park |


