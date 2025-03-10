from flask import Flask, redirect, url_for, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib.pyplot as plt
import io, base64
import calendar

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.String(25))
    type = db.Column(db.String(50), nullable=False)

# with app.app_context():
#     db.create_all()

@app.route("/", methods=["POST", "GET"])
def index():

    if request.method == "POST":
        
        amount = request.form.get('amount')
        type = request.form.get('tag')
        desc = request.form.get('description')
        date = request.form.get('date')

        if amount == "":
            amount = 0
        else:
            amount = int(amount)

        if amount != 0 and desc != "" and date != "":
            
            new_expense = Expenses(amount=amount, desc=desc, date_created=date, type=type)

            try:
                db.session.add(new_expense)
                db.session.commit()
                return redirect("/")
            except:
                return "Error in adding expense."

        else:
            return "Either amount or description or date is missing."

    else:
        expenses = Expenses.query.order_by(Expenses.date_created).all()
        return render_template('index.html', expenses=expenses)

@app.route("/delete/<int:id>")
def delete(id):

    expense = Expenses.query.get_or_404(id)

    try:
        db.session.delete(expense)
        db.session.commit()
        return redirect("/")
    except:
        return "Error in deleting expense."
    
@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):

    expense = Expenses.query.get_or_404(id)

    if request.method == "POST":
        new_amt = request.form.get('amount')
        new_date = request.form.get('date')
        new_type = request.form.get('tag')
        new_desc = request.form.get('description')

        if new_amt == "":
            new_amt = 0
        else:
            new_amt = int(new_amt)

        if new_amt != 0 and new_desc != "" and new_date != "":
            expense.amount = new_amt
            expense.date_created = new_date
            expense.desc = new_desc
            expense.type = new_type

            try:
                db.session.commit()
                return redirect("/")
            except:
                return "Error in updating expense."

        else:
            return "Either amount or description or date is missing."
        
    else:
        return render_template('update.html', expense=expense)
    
@app.route("/graphs/monthly")
def monthly_graphs():

    month = datetime.now().month
    year = datetime.now().year

    expenses = Expenses.query.all()

    this_month_expense = [
        expense for expense in expenses
        if datetime.strptime(expense.date_created, "%Y-%m-%d").month == month and
        datetime.strptime(expense.date_created, "%Y-%m-%d").year == year
    ]

    if len(this_month_expense) > 0:

        food_total = 0
        bill_total = 0
        travel_total = 0
        misc_total = 0
        enter_total = 0

        for exp in this_month_expense:

            if exp.type == "Food":
                food_total += exp.amount
            if exp.type == "Travel":
                travel_total += exp.amount
            if exp.type == "Bills":
                bill_total += exp.amount
            if exp.type == "Entertainment":
                enter_total += exp.amount
            if exp.type == "Miscellaneous":
                misc_total += exp.amount

        amounts = [food_total, travel_total, bill_total, misc_total, enter_total]
        labels = [f"Food, {food_total}", f"Travel, {travel_total}", f"Bills, {bill_total}", f"Miscellaneous, {misc_total}", f"Entertainment: {enter_total}"]

        img = io.BytesIO()
        fig = plt.figure(figsize=(10, 7))
        plt.pie(amounts, labels=labels)
        plt.savefig(img, format='png')
        img.seek(0)
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

        Month = calendar.month_name[month]

        title = f"Monthly Graph of Expenses for {Month}"

        return render_template('graph_month.html', img=img_base64, title=title)
    
    else:
        return "No Expenses for the current Month."
    
@app.route("/download/pdf")
def download():

    docTitle = 'expenses'
    title = 'All Expenses'

    expenses = Expenses.query.order_by(Expenses.date_created).all()

    pdf_bytes = io.BytesIO()
    pdf = canvas.Canvas(pdf_bytes)
    
    pdf.setTitle(docTitle)
    pdfmetrics.registerFont(
        TTFont('font', 'assets/font.ttf')
    )

    pdf.setFont('font', 40)
    pdf.drawCentredString(300, 770, title)
    pdf.line(30, 710, 550, 710)

    text = pdf.beginText(20, 680)
    text.setFont("Helvetica", 12)

    for expense in expenses:
        text.textLine(f"Amount: {expense.amount} | Type: {expense.type} | Date: {expense.date_created} | Desc: {expense.desc}")

    pdf.drawText(text)
    pdf.save()

    pdf_bytes.seek(0)

    return send_file(pdf_bytes, as_attachment=True, download_name="Expenses.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)