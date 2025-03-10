from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now)

# with app.app_context():
#     db.create_all()

@app.route("/", methods=["POST", "GET"])
def index():

    if request.method == "POST":
        task_text = request.form['text']

        if task_text != "":
            new_task = Tasks(text=task_text)

            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect("/")

            except:
                return "Error in adding Task."
            
        else:
            return "Empty Tasks cannot be added."
        
    else:
        tasks = Tasks.query.order_by(Tasks.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id):

    task_to_delete = Tasks.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")

    except:
        return "Error in deleting Task."

@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):

    task = Tasks.query.get_or_404(id)

    if request.method == "POST":
        task.text = request.form['text']

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error in updating Task."

    else:
        return render_template('update.html', task=task)

@app.route("/toggle/<int:id>")
def toggle(id):

    task = Tasks.query.get_or_404(id)

    if task.completed == 0:
        task.completed = 1
    else:
        task.completed = 0

    try:
        db.session.commit()
        return redirect("/")
    except:
        return "Error in toggling Task."
    
@app.route("/up/<int:id>")
def up(id):

    task = Tasks.query.get_or_404(id)

    if id > 1:
        upper = Tasks.query.get_or_404(id - 1)
        task.text, upper.text = upper.text, task.text

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error in moving Task up."
        
    else:
        return "Cannot be moved up."

@app.route("/down/<int:id>")
def down(id):

    task = Tasks.query.get_or_404(id)
    num = Tasks.query.count()

    if id < num:
        lower = Tasks.query.get_or_404(id + 1)

        task.text, lower.text = lower.text, task.text

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error in moving Task down."
        
    else:
        return "Cannot be moved down."
       
if __name__ == "__main__":
    app.run(debug=True)