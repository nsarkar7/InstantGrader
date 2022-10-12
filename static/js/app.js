var classes_list = {};
var questions_added = 0;

function login_check() {
    if(sessionStorage.getItem("name") === null || sessionStorage.getItem("email") === null || sessionStorage.getItem("picture") === null){
        window.location.replace("/")
    }
    else {
        display_user_info();
    }
}

function display_user_info() {
    let name = sessionStorage.getItem("name");
    let email = sessionStorage.getItem("email");
    let picture = sessionStorage.getItem("picture");
    document.getElementById("profile_button_text").innerHTML = name;
    document.getElementById("profile_button_img").src = picture;
}

function display_assignments(class_name) {

    let selected_class = null;
    let assignments = null;

    for(let i=0; i<classes_list.length; i++) {
        let individual_class = classes_list[i];
        if(class_name == individual_class.class_name){
            selected_class = individual_class;
            assignments = selected_class.assignments;
            console.log("sus");
            break;
        }
    }
    if(assignments.length == 0) {
        if(document.getElementById("no_assignments_text") == undefined){
            let main = document.getElementById("main");
            let no_assignments_text = document.createElement("h3")
            no_assignments_text.innerHTML = "Looks like you have not assigned anything yet. Use the button above to create a new one."
            no_assignments_text.className = "no_assignments_text";
            no_assignments_text.id = "no_assignments_text";
            main.appendChild(no_assignments_text);
        }
    }
    for(let i=0; i<assignments.length; i++) {
        let main = document.getElementById("main");
        let assignment_btn = document.createElement("button");
        assignment_btn.innerHTML = individual_class.class_name;
        assignment_btn.className = "assignment_button";
        sidebar.appendChild(class_btn);
    }
    
    
}

function get_classes() {
    let teacher_id = sessionStorage.getItem("id");

    get_classes_request = new XMLHttpRequest();

    get_classes_request.onreadystatechange = function() {
        if (this.status == 200 && this.readyState == 4) {
            let classes = JSON.parse(this.responseText);
            classes_list = classes;
            for(let i=0; i<classes.length; i++){
                let individual_class = classes[i];
                let sidebar = document.getElementById("sidebar");
                let class_btn = document.createElement("button");
                class_btn.innerHTML = individual_class.class_name;
                class_btn.className = "class_button";
                class_btn.onclick = () => display_assignments(individual_class.class_name);
                sidebar.appendChild(class_btn);
            }
        }
    }
    
    link = "/get_classes?teacher_id=" + teacher_id;
    console.log(link)
    get_classes_request.open("GET", link);

    get_classes_request.send();

}

function create_new_class() {
    let class_name = document.getElementById("class_name").value;
    let class_password = document.getElementById("class_pwd").value;
    let teacher_id = sessionStorage.getItem("id");

    new_class_request = new XMLHttpRequest();

    new_class_request.onreadystatechange = function() {
        if (this.status == 201) {
        }
    }

    link = "/new_class?class_name=" + class_name + "&class_password=" + class_password + "&teacher_id=" + teacher_id;

    new_class_request.open("GET", link);

    new_class_request.send();
}
