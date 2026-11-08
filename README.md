# CleanConnect

A civic issue reporting and tracking system where citizens report local problems such as garbage, road damage, water leakage and street light faults. Admins review and update the status of each complaint.

## Features
- User registration and login
- Submit complaints with issue type, description, photo and map location
- Interactive map (Leaflet.js) to mark the exact location of an issue
- Track complaint status: Pending, In Progress, Resolved
- Admin login to view and manage all complaints
- Passwords stored as secure hashes

## Tech Stack
- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Maps:** Leaflet.js

## Project Structure
- `app.py` – main Flask application
- `config.py` – database settings
- `database.sql` – database schema and sample data
- `templates/` – HTML pages
- `static/` – CSS, JavaScript and uploaded images

## How to Run
1. Install Python and MySQL.
2. Install the libraries: `pip install -r requirements.txt`
3. Run `database.sql` in MySQL Workbench to create the database and sample data.
4. Open `config.py` and set your own MySQL username and password.
5. Start the app: `python app.py`
6. Open `http://localhost:5000` in your browser.

## Demo Logins
- **Admin:** username `admin`, password `Admin@123`
- **User:** email `rahul@example.com`, password `Test@1234`

## Author
Christa Ann Alex
