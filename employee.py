from flask import Blueprint
from connection import Connection

show_employee = Blueprint('show_employee', __name__, static_folder='static', template_folder='templates')


@show_employee.route('/employee/<int:id>', methods=['GET', 'POST'])
def employee(id):
    db = Connection()
    emp = str(db.find_employee_by_id(id))
    return emp
