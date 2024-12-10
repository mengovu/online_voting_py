import uuid
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this for production use

# In-memory storage for votes
candidates = {"Junaid": 7, "Rakshitha": 10, "Abhijeet": 0, "Harshitha": 17, "Shrihari": 25}

# In-memory storage for users with admin credentials
users = {
    "admin": {"id": str(uuid.uuid4()), "password": "adminpass", "role": "admin", "age": 30},
    # Add your new admin user below
    "new_admin": {"id": str(uuid.uuid4()), "password": "newadminpass", "role": "admin", "age": 40}
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = int(request.form['age'])

        if username in users:
            return "Username already exists, please choose another."

        # Store new user with a unique ID
        users[username] = {"id": str(uuid.uuid4()), "password": password, "role": "user", "age": age}
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        if user and user['password'] == password:
            session.clear
            session['username'] = username
            session['role'] = user['role']
            session['age'] = user['age']
            #session['user_id'] = user['id']
            session['voted'] = False
            return redirect(url_for('vote'))
        else:
            return "Invalid credentials, please try again."
    
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect(url_for('login'))

    if session.get('role') == 'admin':
        return redirect(url_for('results'))

    if session.get('voted') is True:
        return "You have already voted!"

    if session['age'] < 18:
        return "You must be 18 or older to vote."

    if request.method == 'POST':
        selected_candidate = request.form.get('candidate')
        
        if selected_candidate in candidates:
            candidates[selected_candidate] += 1
            session['voted'] = True
            return "Thank you for voting!"

    return render_template('vote.html', candidates=candidates)

@app.route('/results')
def results():
    if 'username' not in session or session.get('role') != 'admin':
        return "You are not authorized to view the results."

    return render_template('results.html', candidates=candidates)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return "Access Denied. Admins only."

    # Calculate total votes
    total_votes = sum(candidates.values())

    return render_template('dashboard.html', 
                           candidates=candidates, 
                           total_votes=total_votes,
                           user_role=session.get('role'),
                           username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
