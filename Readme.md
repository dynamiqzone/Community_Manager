

# YOUR PROJECT TITLE:
    Project Overview: CommunityHub Digital Management System

# GutHub Link:
https://github.com/dynamiqzone/Community_Manager


#### Video Demo: <Link to your YouTube Video>
#### Author: 
Rahil Nasim (GitHub: dynamiqzone) (EdEx: SS_2510_SF4C) (dynamiqzone@gmail.com) 



I tried to follow the industry level foot print by creating the plan in a way that follows in most industry although I did not use any software but i am learning towards it. For the sake of time I only planned it and used this for developing this Final Project.

#### Description:
CommunityHub: Digital Management System

What is this project?
I built CommunityHub because I noticed that most small clubs and charities around here usually run their entire organization out of a messy WhatsApp group or a shared Excel sheet that always gets outdated. I wanted to create a central spot where a leader could actually manage the "boring" stuff like tracking who paid their dues and who is actually showing up to volunteer without it being a total headache.

The app is a full-stack project built with Flask and SQLAlchemy. It’s designed to give different levels of access to different people, members can sign up for events, while supervisors and admins handle the background work like updating the community announcement bar or recording payments.

Why I did it this way (Design Choices)
When I was designing the database and the logic, I made a few specific choices based on how I thought a real club would use it:

The Founder Logic: I didn't want to have to manually create an admin account in the database every time. So, I wrote logic where the very first person who registers on a fresh install is automatically set as the "Founder." This person has the power to promote others to Admin or Supervisor roles. It's not the most complex system, but it works for getting a community started.

Strings for Dates: I decided to store event dates and times as simple strings (db.String) instead of using complex DateTime objects. While I know DateTime is more professional, using strings made it way easier to work with the HTML date-pickers and saved me from fighting with timezone bugs, which was a trade off I made so I could focus more on the volunteer logic.

SQLite for Portability: I stuck with SQLite because I was moving my files back and forth between different setups. Having everything in a single users.db file made it much easier to keep my data consistent without setting up a whole server.

Technical Stuff
The backend is all Python and Flask. For security, I used Werkzeug to hash passwords so they aren't just sitting there in plain text. One part I’m actually pretty proud of is the custom access control. I used Python decorators (@login_required and @admin_required) to wrap my routes. It keeps the code looking clean and makes sure a regular member can't just stumble into the Admin panel by guessing the URL.

Development Challenges (The Real Story)
This project gave me a lot of trouble when I switched my development environment. I originally started on Windows/WSL, but when I moved everything over to a native Linux Mint install, I hit a massive wall with PEP 668. I couldn't install any of my requirements because Mint protects its system Python. I had to learn how to properly set up a .venv (virtual environment) and link it to my terminal, which was a huge learning curve that I wasn't expecting.

I also spent way too much time debugging my helpers.py file. Refactoring it and getting the logic to correctly check for multiple roles—Admin, Supervisor, and Treasurer was probably the most satisfying part of the whole build, even if it was frustrating at the time.

Future Improvements
If I had more time, I’d definitely add:

JavaScript: Right now, the page refreshes every time you RSVP. It would be cool to use some basic JS so it happens instantly.

Live Payments: Maybe integrating Stripe / Braintree so the "Record Payment" feature actually handles real money instead of just being a manual ledger.

Password Reset: Currently, if someone forgets their password, I have to manually help them in the database. An automated email reset would be the next big step.

# Project Plan: 
The "Community Impact" Project: Local Charity/Club Manager
The Problem: Many small local organizations (sports teams, charities, book clubs) manage everything through messy WhatsApp chats or Excel sheets.

The main goal of CommunityHub is to act as a Digital Bridge. It takes a disorganized group of people (who usually use messy group chats) and gives them a Structured System to manage three things: Identity, Action, and Money.



The Features: * Member registration and login.

An event calendar where members can RSVP.

A "Dues/Donations" tracker (similar to your Finance ledger).

An Admin dashboard to post announcements.

---

## **Epic 1: Identity & Access Management (The Gatekeeper)**

*Goal: Ensure only authorized users can interact with the community.*

### **Story 1.1: User Registration**

* **Task A:** Design `register.html` with fields for `username`, `password`, `confirmation`, and `full_name`.
* **Task B:** Write Flask route to validate password match and unique username.
* **Task C:** Implement SQL `INSERT` to store hashed passwords in the `users` table.

### **Story 1.2: Secure Authentication**

* **Task A:** Design `login.html` with `username` and `password` inputs.
* **Task B:** Write Flask route using `check_password_hash` to verify credentials.
* **Task C:** Store `user_id` and `role` in the Flask `session` object.

### **Story 1.3: Access Control (Security)**

* **Task A:** Create `login_required` decorator in `helpers.py`.
* **Task B:** Create `admin_required` decorator to check if `session["role"] == 'admin'`.

---

## **Epic 2: Event Infrastructure (The Calendar)**

*Goal: Give the community a place to see and create activities.*

### **Story 2.1: Admin Event Creation**

* **Task A:** Create a restricted `add_event.html` form with Date/Time inputs.
* **Task B:** Write POST route to save new events to the `events` table.
* **Task C:** Implement "Success" flash messages after creation.

### **Story 2.2: The Community Feed**

* **Task A:** Write SQL query to fetch all events sorted by date.
* **Task B:** Design `index.html` using Bootstrap Cards to display event details.
* **Task C:** Handle the "Empty State" (UI for when no events are scheduled).

---

## **Epic 3: Member Engagement (The Interaction)**

*Goal: Convert passive viewers into active participants.*

### **Story 3.1: RSVP Logic**

* **Task A:** Add a "Going" button to the event cards.
* **Task B:** Write POST route to record user/event pairs in the `rsvps` table.
* **Task C:** Prevent duplicate RSVPs using SQL `UNIQUE` constraints or conditional checks.

### **Story 3.2: Attendance Tracking**

* **Task A:** Create an "Event Detail" page showing a list of who is attending.
* **Task B:** Implement a "Cancel RSVP" feature for members.

---

## **Epic 4: Financial Integrity (The Ledger)**

*Goal: Centralize the tracking of money for transparency.*

### **Story 4.1: Payment Logging (Admin Only)**

* **Task A:** Create a form to select a user and input a dollar amount.
* **Task B:** Save the transaction with a timestamp to the `transactions` table.

### **Story 4.2: Personal Ledger (Member)**

* **Task A:** Design a "My Dues" page for logged-in users.
* **Task B:** Write SQL query to `SUM` all payments made by the current user.
* **Task C:** Display a table of payment history sorted by most recent.

---

## **Epic 5: Production Readiness (The Launch)**

*Goal: Polish the app for the CS50 submission.*

### **Story 5.1: Global UI/UX Polish**

* **Task A:** Build a responsive `layout.html` with a dynamic Navbar (showing different links for Admin vs. Member).
* **Task B:** Add custom CSS for branding (colors, fonts).

### **Story 5.2: Final Documentation**

* **Task A:** Write the 750-word `README.md` explaining file structure and design choices.
* **Task B:** Film and edit the 3-minute video demonstration.

---

# The Files in my Project:

app.py: This is where almost all my code is. It handles all the routes like /login, /register, and /add_event. I spent a lot of time in here writing the SQL queries to make sure that only the right data shows up for the right person.

helpers.py: I put my decorators here. These are the "security guards" of the app. I wrote @login_required and @admin_required so that I didn't have to write the same security check over and over again in app.py.

instance>users.db: This is my SQLite database. It has tables for users, events, rsvps, and transactions. I like SQLite because it’s just one file, which made it easier when I moved my project to Linux.

templates folder: This has all my HTML. I used Jinja2 to make it dynamic. For example, the navbar changes depending on if you are an Admin or just a regular Member.

static folder: This has my styles.css. I'm not a pro at CSS, so I used a lot of Bootstrap, but I added some custom styles to fix things like the background height and button colors.

