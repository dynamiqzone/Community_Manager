from flask import Flask, render_template

app = Flask(__name__)

# Temporary route to preview ANY template
@app.route('/preview/<page>')
def preview(page):
    # This will look for 'register.html' if you go to /preview/register.html
    return render_template(page)

if __name__ == '__main__':
    app.run(debug=True)
