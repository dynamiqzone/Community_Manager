from flask import Flask, render_template

app = Flask(__name__)

# Temporary route to preview ANY template
@app.route('/register')
def register():
    # This will look for 'register.html' if you go to /preview/register.html
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
