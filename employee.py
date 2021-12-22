from flask import Blueprint, render_template, request, jsonify 
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
    
    else:
        new_title = request.json.get('title')
        return jsonify({ 'result': "OK" })

@show_employee.route('/employee/title/<int:id>', methods=['GET'])
def employee_title(id):
    db = Connection()

    return render_template("edit_form.html", edit_title="TITLE", emp_id=id)

@show_employee.route('/employee/boss/<int:id>', methods=['GET'])
def employee_boss(id):
    db = Connection()

    return render_template("edit_form.html", edit_title="BOSS", emp_id=id)

@show_employee.route('/employee/remove/<int:id>', methods=['GET'])
def employee_remove(id):
    db = Connection()

    return render_template("edit_form.html", edit_title="REM", emp_id=id)
