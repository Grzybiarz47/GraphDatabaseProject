function toListAll(){
    window.location.href = "/employee";
}
function toSetBoss(emp_id){
    window.location.href = "/employee/boss/" + emp_id.toString();
}
function toSetTitle(emp_id){
    window.location.href = "/employee/title/" + emp_id.toString();
}
function toRemoveEmp(emp_id){
    window.location.href = "/employee/remove/" + emp_id.toString();
}
function toAddNewEmp(){
    window.location.href = "/hire";
}
function putMethod(emp_id){
    url = "/employee/" + emp_id.toString()
    title = document.getElementById("title").value

    fetch(url, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'title' : title})})
        .then(response => response.json())
        .then(data => console.log(data));

    window.location.href = url
}
function deleteMethod(emp_id, rem){
    url = "/employee/" + emp_id.toString()

    fetch(url, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'rem' : rem})})
        .then(response => response.json())
        .then(data => console.log(data));

    if(rem == true)
        window.location.href = '/index'
    else
        window.location.href = url
}