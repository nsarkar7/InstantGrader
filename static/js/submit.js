var path = window.location.pathname;

var nodeList = path.split('/')

var teacher_id = nodeList[3];
var class_name = nodeList[4];
var assignment_name = nodeList[5];

class_name = class_name.replaceAll('%20', ' ');
assignment_name = assignment_name.replaceAll('%20', ' ');


function display_assignment_info() {
    let assignment_name_text = document.getElementById("assignments_text");
    assignment_name_text.innerHTML = assignment_name;

    let classes_text = document.getElementById("classes_text");
    classes_text.innerHTML = class_name;
}
