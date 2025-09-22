# HTTP Server & Client
This project started as a university lab assignment where I built a simple HTTP/1.1 compliant server and client from scratch in Python.
I have since extended it to a personal cybersecurity project to explore how real web servers handle attacks and defenses.

## Features
- The HTTP/1.1 server serves static HTML & CSS from a local www directory.
- The HTTP client can send GET and POST requests (to both my custom server and to standard servers).
- Handles basic HTTP status codes such as 200, 301, 404, 405, 500.

## Security Learning Extensions
As I extend this project, I'm documenting my process with three main types of notes:
- threat_model.md: Brainstorming possible threats to the server and outlining defenses.
- logs/: A folder for experiment logs with dates, what I tested, what happened, and what I learned.
- experiments/: A folder for test scripts, malicious inputs, and generally any code I use to attack or defend my server.

## Acknowledgements
This project originated as part of the CMPUT 404: Web Applications and Architecture course at the University of Alberta.
The lab specification is available [here](https://uofa-cmput404.github.io/labsignments/http.html).
Lab designed and published by:
- Hazel Victoria Campbell
- Samuel Iwuchukwu
- Sadia Zahin Prodhan