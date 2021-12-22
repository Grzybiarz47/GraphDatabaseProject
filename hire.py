from flask import Blueprint, render_template, redirect, request 
from connection import Connection

add_employee = Blueprint('add_employee', __name__, static_folder='static', template_folder='templates')

@add_employee.route('/hire', methods=['GET', 'POST'])
def hire():
    db = Connection()

    if request.method == 'POST':
        new_employee = {
            "first":request.form.get("first"),
            "last":request.form.get("last"),
            "title":request.form.get("title"),
            "nation":request.form.get("nation"),
            "born":request.form.get("born"),
            "start":request.form.get("start")
        }
        boss = request.form.get("boss")

        if new_employee.get("first") and new_employee.get("last") and new_employee.get("title") and boss:
            boss = boss.split(' ')[3]
            new_employee["card_id"] = db.next_card_id()
            
            return render_template('index.html', info="Dodano nowego pracownika")

        else:
            return render_template('index.html', info="Nie udało się dodać nowego pracownika - brak kluczowego parametru")

    if request.method == 'GET':
        all = db.list_all()
        all = [emp["firstname"] + " " + emp["lastname"] + " " + emp["title"] + " " + str(emp["card_id"]) for emp in all]
        return render_template('hire_form.html', selection=all)