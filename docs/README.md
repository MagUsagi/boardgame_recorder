# Board Game Recorder

## Overview
The **Board Game Recorder** is a web application designed to effortlessly track board game play history, player statistics, and game details. Built with Django, the app allows users to log game sessions, record player scores, and visualize play data — providing an intuitive way to manage board game collections and gameplay history.

This project highlights my full-stack development skills, with a strong focus on backend logic, database design, and user interface responsiveness. It also serves as a portfolio piece showcasing my ability to build, deploy, and manage web applications.

---

## Features

### Game Management
- **Add Games**: Input game details — including title, image, description, player count, duration, categories, and optional expansions.
- **Game Detail Pages**: View detailed information about each game, including past play records.
- **Dynamic Expansions**: Add expansions linked to their respective games.

### Game Sessions & Results
- **Record Game Sessions**: Log game plays by selecting a game, play date, duration, and whether expansions were used.
- **Track Player Results**: Enter player names, scores, and mark winners.
- **Accordion-Style Record**: Game record is shown in collapsible sections, sorted by the most recent play date.

### Player Tracking
- **Add Players**: Add new players via a responsive modal form.
- **Player Profiles**: View a player's recent games, total wins, and other stats (planned feature).

### Responsive Design
- Optimized for mobile and desktop views.
- Clean UI ensuring seamless user experience on all devices.

---

## Tech Stack

- **Backend**: Django(Python)
- **Frontend**: HTML, Bootstrap, CSS, JavaScript (with AJAX for dynamic interactions)
- **Database**: SQLite (for development)
- **Deployment**: Local (Linux server)
- **Version Control**: Git & GitHub

---

## Future Improvements
- **Player Profiles**: Dedicated pages showing detailed player stats and game history.
- **Data Visualization**: Graphs for win rates, most-played games, and player rankings.
- **Enhanced Filters**: Search games by category, player count, or playtime.
- **Monthly Reports**: Generate monthly summaries of games played and top players.

---

## How to Run the Project (Development)

1. Clone the repository:
```bash
git clone <repository_url>
cd boardgame_recorder
```
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Apply database migrations:
```bash
python manage.py migrate
```
5. Run the server:
```bash
python manage.py runserver
```
6. Access the app at `http://localhost:8000`

---

## Contact
If you'd like to connect or discuss this project, feel free to reach out!

- **LinkedIn**: [LinkedIn Profile](https://www.linkedin.com/in/akane-klauenboesch/)
- **GitHub**: [GitHub Profile](https://github.com/MagUsagi/)

---

## Acknowledgments
This project was inspired by my passion for board games and web development. It reflects both my technical skills and my desire to build tools that enhance user experiences.

---

Thank you for visiting the **Board Game Recorder**!

