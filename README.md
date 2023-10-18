# EvaDB Project 1: AI Search Engine
## How to run
Make sure that virtual environment is activated, and all the required dependencies present in requirements.txt are installed.
```
python ai_search_engine.py
```

## Few example queries
### Example 1: With Summarization Enabled
```
Query: Tell me about sports
Summary:
Golf is a club-and-ball sport in which players use various clubs to hit a ball into a series of holes on a course in as few strokes as possible. The modern game of golf originated in 15th century Scotland. Golfs first major, and the worlds oldest golf tournament, is The Open Championship, also known as the British Open, which was first played in 1860.
docs/golf.txt
Relevant Text 0
Golf, unlike most ball games, cannot and does not use a standardized playing area, and coping with the varied terrains encountered on different courses is a key part of the game. Courses typically have either 9 or 18 holes, regions of terrain that each contain a cup, the hole that receives the ball. Each hole on a course contains a teeing ground to start from, and a putting green containing the cup. There are several standard forms of terrain between the tee and the green, such as the fairway, rough (tall grass), and various hazards such as water, rocks, or sand-filled bunkers. Each hole on a course is unique in its specific layout.
Relevant Text 1
The modern game of golf originated in 15th century Scotland. The 18-hole round was created at the Old Course at St Andrews in 1764. Golfs first major, and the worlds oldest golf tournament, is The Open Championship, also known as the British Open, which was first played in 1860 at the Prestwick Golf Club in Ayrshire, Scotland. This is one of the four major championships in mens professional golf, the other three being played in the United States: The Masters, the U.S. Open, and the PGA Championship.
Relevant Text 2
Golf is played for the lowest number of strokes by an individual, known as stroke play, or the lowest score on the most individual holes in a complete round by an individual or team, known as match play. Stroke play is the most commonly seen format at all levels, especially at the elite level.
Relevant Text 3
Golf is a club-and-ball sport in which players use various clubs to hit a ball into a series of holes on a course in as few strokes as possible.
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
docs/Cricket.pdf
Relevant Text 0
Cricket has three formats- T20, ODI and test. T20, also known as 20-20 is played for 20 overs by each team like IPL or Indian Premier League. ODI or One Day International is played for 50 over by each team and lasts the whole day. The test format is played for five days by the two teams with at least 90 overs per day.
Relevant Text 1
```

### Example 2: Without Summarization
```
Query: Tell me about sports
docs/golf.txt
Relevant Text 0
Golf, unlike most ball games, cannot and does not use a standardized playing area, and coping with the varied terrains encountered on different courses is a key part of the game. Courses typically have either 9 or 18 holes, regions of terrain that each contain a cup, the hole that receives the ball. Each hole on a course contains a teeing ground to start from, and a putting green containing the cup. There are several standard forms of terrain between the tee and the green, such as the fairway, rough (tall grass), and various hazards such as water, rocks, or sand-filled bunkers. Each hole on a course is unique in its specific layout.
Relevant Text 1
The modern game of golf originated in 15th century Scotland. The 18-hole round was created at the Old Course at St Andrews in 1764. Golfs first major, and the worlds oldest golf tournament, is The Open Championship, also known as the British Open, which was first played in 1860 at the Prestwick Golf Club in Ayrshire, Scotland. This is one of the four major championships in mens professional golf, the other three being played in the United States: The Masters, the U.S. Open, and the PGA Championship.
Relevant Text 2
Golf is played for the lowest number of strokes by an individual, known as stroke play, or the lowest score on the most individual holes in a complete round by an individual or team, known as match play. Stroke play is the most commonly seen format at all levels, especially at the elite level.
Relevant Text 3
Golf is a club-and-ball sport in which players use various clubs to hit a ball into a series of holes on a course in as few strokes as possible.
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
docs/Cricket.pdf
Relevant Text 0
Cricket has three formats- T20, ODI and test. T20, also known as 20-20 is played for 20 overs by each team like IPL or Indian Premier League. ODI or One Day International is played for 50 over by each team and lasts the whole day. The test format is played for five days by the two teams with at least 90 overs per day.
Relevant Text 1
The team that bats first sets a target score which the other side should chase down. If the team chases down the score, they win. If the scores are tied, a final over called the super over is played by the sides. The team that scores the highest runs or chases down the target score wins. In case of weather problems, then the match is either cancelled or the Duckworth- Lewis method is adopted. Here the score of the teams at last over that was played is compared. The team with the highest runs wins.
```

### Example 3: Enable Summarization
```
Query: ENABLE SUMMARY
Summarization enabled!
```

### Example 4: Disable Summarization
```
Query: DISABLE SUMMARY
Summarization disabled!
```

### Example 5: Set Limit for Number of Relevant Paragraphs Returned
```
Query: LIMIT 20
Limit set to 20
```

### Example 6: SHOW table used by Search Engine
```
Query: SHOW

    mydocuments._row_id       mydocuments.name  mydocuments.page  mydocuments.paragraph                                   mydocuments.data
0                     1        docs/tennis.txt                 1                      1  Tennis is a racket sport that is played either...
1                     2        docs/tennis.txt                 1                      2  Tennis is an Olympic sport and is played at al...
2                     3        docs/tennis.txt                 1                      3  The rules of modern tennis have changed little...
3                     4        docs/tennis.txt                 1                      4  Tennis is played by millions of recreational p...
4                     5        docs/soccer.txt                 1                      1  Association football, more commonly known as f...
5                     6        docs/soccer.txt                 1                      2  The game of association football is played in ...
6                     7        docs/soccer.txt                 1                      3  Internationally, association football is gover...
7                     8          docs/golf.txt                 1                      1  Golf is a club-and-ball sport in which players...
8                     9          docs/golf.txt                 1                      2  Golf, unlike most ball games, cannot and does ...
9                    10          docs/golf.txt                 1                      3  Golf is played for the lowest number of stroke...
10                   11          docs/golf.txt                 1                      4  The modern game of golf originated in 15th cen...
11                   12  docs/table_tennis.txt                 1                      1  Table tennis (also known as ping-pong) is a ra...
12                   13  docs/table_tennis.txt                 1                      2  Owed to its small minimum playing area, its ab...
13                   14  docs/table_tennis.txt                 1                      3  Table tennis has been an Olympic sport since 1...
14                   15  docs/table_tennis.txt                 1                      4  Table tennis is governed by the International ...
15                   16      docs/Swimming.pdf                 1                      1                                           Swimming
16                   17      docs/Swimming.pdf                 1                      2  Swimming is an individual or team racing sport...
17                   18      docs/Swimming.pdf                 1                      3  Swimming each stroke requires a set of specifi...
18                   19        docs/Hockey.pdf                 1                      1                                             Hockey
19                   20        docs/Hockey.pdf                 1                      2  Hockey is a term used to denote a family of va...
...
```

### Example 7: Database also gets updated automatically at intervals of 1 minute
```
Updated the database!
Added docs/football.txt
Removed docs/soccer.txt
```

### Example 8: Exit the program
```
Query: exit
Exiting...
```

## More Details
For more details including features and implementation, please check `Report.pdf`.