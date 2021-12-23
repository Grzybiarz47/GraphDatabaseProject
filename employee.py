from logging import info
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import redirect 
from connection import Connection

show_employee = Blueprint('show_employee', __name__, static_folder='static', template_folder='templates')

@show_employee.route('/employee', methods=['GET', 'POST'])
def list_employees():
    db = Connection()

    if request.method == 'POST':
        first = request.form.get('findNameEmp')
        last = request.form.get('findSurnameEmp')
        emp = db.find_employees_by_name(first, last)
        if emp == []:
            return render_template("index.html", info="Nie znaleziono pracownika " + first + " " + last)
        else:
            return render_template("employee.html", employees=emp)

    if request.method == 'GET':    
        all = db.list_all()
        return render_template("employee.html", employees=all)

@show_employee.route('/employee/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def employee(id):
    db = Connection()
    
    if request.method == 'GET':
        emp = db.find_employee_by_id(id)
        sup = db.list_supervisors(id)
        sub = db.list_direct_subordinates(id)
        return render_template("employee.html", employees=emp, supervisors=sup, subordinates=sub, emp_id=id)
    
    if request.method == 'POST':
        boss = request.form.get("boss").split(' ')
        boss_id = int(boss[-1])
        sup = db.list_supervisors(id)
        cur_boss_id = int(sup[0].get("id"))

        db.remove_relation(cur_boss_id, id)
        db.add_relation(boss_id, id)

        emp = db.find_employee_by_id(id)
        sup = db.list_supervisors(id)
        sub = db.list_direct_subordinates(id)
        return render_template("employee.html", employees=emp, supervisors=sup, subordinates=sub, emp_id=id)
        
    if request.method == 'PUT':
        title = request.json.get('title')
        if title and title != "":
            db.change_title(id, title)
        return jsonify({ 'result': 'OK' })

    if request.method == 'DELETE':
        rem = request.json.get('rem')
        if rem == True:
            db.remove_employee(id)
        return jsonify({ 'result': 'OK' })

@show_employee.route('/employee/title/<int:id>', methods=['GET'])
def employee_title(id):
    return render_template("edit_form.html", edit_title="TITLE", emp_id=id)

@show_employee.route('/employee/boss/<int:id>', methods=['GET'])
def employee_boss(id):
    db = Connection()
    all = db.list_all()
    all = filter(lambda x : x["card_id"] != id, all)
    all = [emp["firstname"] + " " + emp["lastname"] + " " + emp["title"] + " " + str(emp["card_id"]) for emp in all]
    sub = db.list_subordinates(id)
    sub = [emp["first"] + " " + emp["last"] + " " + emp["title"] + " " + str(emp["id"]) for emp in sub]

    for emp in sub:
        if emp in all:
            all.remove(emp)

    if all == []:
        return render_template('index.html', info="Brak możliwości wyboru przełożonych dla tego pracownika")
    else:
        return render_template("edit_form.html", edit_title="BOSS", selection=all, emp_id=id)

@show_employee.route('/employee/remove/<int:id>', methods=['GET'])
def employee_remove(id):
    db = Connection()
    sub = db.list_direct_subordinates(id)
    if sub != []:
        return render_template('index.html', info="Pracownika posiada podwładnych. Należy najpierw zmienić przełożonego wszystkim podwładnym.")
    else:
        return render_template("edit_form.html", edit_title="REM", emp_id=id)
