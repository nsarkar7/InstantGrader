var selected_class_name = null;
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

function add_answer() {
    let table = document.getElementById("answers_table");
    let table_row = table.insertRow(questions_added);

    let text_cell = table_row.insertCell(0);
    let input_cell = table_row.insertCell(1);

    let input = document.createElement("input");
    input.setAttribute('type',"text");
    input.className = "table_input_cell";
    text_cell.innerHTML = "Answer " + (questions_added+1) + ":";
    input_cell.appendChild(input);
    questions_added++;
}


function american_date_format(date) {
    let year = date.substring(0, 4);
    let month = date.substring(5, 7);
    let day = date.substring (8, 10);
    let new_date = month + "/" + day + "/" + year;
    return new_date;
}



function display_user_info() {
    let name = sessionStorage.getItem("name");
    let email = sessionStorage.getItem("email");
    let picture = sessionStorage.getItem("picture");
    document.getElementById("profile_button_text").innerHTML = name;
    document.getElementById("profile_button_img").src = picture;
}

function display_assignments(class_name) {
    document.querySelectorAll('.no_assignments_text').forEach(e => document.getElementById("main").removeChild(e))
    document.querySelectorAll('.assignment_button').forEach(e => document.getElementById("main").removeChild(e))
    get_classes();
    let assignments = [];
    let selected_class = null;

    for(let i=0; i<classes_list.length; i++) {
        let individual_class = classes_list[i];
        if(class_name == individual_class.class_name){
            selected_class = individual_class;
            selected_class_name = selected_class.class_name;
            assignments = selected_class.assignments;
            
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
        let assignment = assignments[i];
        let main = document.getElementById("main");
        let assignment_btn = document.createElement("button");
        let icon = document.createElement("button");   
        let name_text = document.createElement("h3");
        let due_date_text = document.createElement("h3");
        let link_button = document.createElement("button");
        let link_button_container = document.createElement("div");
        
        icon.innerHTML = "<i class=\"fa-solid fa-book fa-2x\"></i>";
        icon.id = "assignments_button_icon";
        link_button_container.id = "assignments_button_link_button_container"
        name_text.id = "assignments_button_name_text";
        due_date_text.id = "assignments_button_due_date_text"
        link_button.id = "assignments_button_link_button"
        name_text.innerHTML = assignment.assignment_name;
        due_date_text.innerHTML = american_date_format(assignment.due_date);
        link_button.innerHTML = "Copy Student Link"
        link_button.onclick = function() {
            navigator.clipboard.writeText(window.location.host + assignment.submit_link);
        };

        assignment_btn.className = "assignment_button";
        assignment_btn.onclick = function(){view_results(assignment.assignment_name)};
        assignment_btn.appendChild(icon);
        assignment_btn.appendChild(name_text);
        assignment_btn.appendChild(due_date_text);
        assignment_btn.appendChild(link_button_container);
        link_button_container.appendChild(link_button);
        main.appendChild(assignment_btn);
    }
    
    
}

function get_classes() {

    document.querySelectorAll('.class_button').forEach(e => document.getElementById("sidebar").removeChild(e))

    let teacher_id = sessionStorage.getItem("id");

    get_classes_request = new XMLHttpRequest();

    let link = "/get_classes?teacher_id=" + teacher_id;
    get_classes_request.open("GET", link, false);

    get_classes_request.send();

    if (get_classes_request.status === 200) { 
            let classes = JSON.parse(get_classes_request.responseText);
            
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

function create_new_class() {
    let class_name = document.getElementById("class_name").value;
    let class_password = document.getElementById("class_pwd").value;
    let teacher_id = sessionStorage.getItem("id");

    new_class_request = new XMLHttpRequest();

    new_class_request.onreadystatechange = function() {
        if (this.status == 201 && this.readyState == 4) {            
            get_classes();

            document.getElementById('new_class_modal').style.display='none';
        }
    }

    let link = "/new_class?class_name=" + class_name + "&class_password=" + class_password + "&teacher_id=" + teacher_id;

    new_class_request.open("GET", link);

    new_class_request.send();

}

function create_assignment() {
    let assignment_name = document.getElementById("assignment_name").value;
    let due_date = document.getElementById("assignment_due_date").value;

    let answers = document.getElementsByClassName("table_input_cell");

    let answers_obj = {};

    for(let i=0; i<answers.length; i++) {
        let answer = answers[i];
        answers_obj[i] = answer.value;
    }

    let answers_json = JSON.stringify(answers_obj);

    let link = "/new_assignment?class_name=" + selected_class_name + "&teacher_id=" + sessionStorage.getItem("id") + "&assignment_name=" + assignment_name + "&due_date=" + due_date + "&answers=" + answers_json;
    
    new_assignment_request = new XMLHttpRequest();

    new_assignment_request.onreadystatechange = function() {
        if (this.status == 201 && this.readyState == 4) {
            display_assignments(selected_class_name);
            
            document.getElementById('new_assignment_modal').style.display='none';
        }
    }

    new_assignment_request.open("GET", link);

    new_assignment_request.send();
}

function view_results(assignment_name) {
    document.querySelectorAll('.result_button').forEach(e => document.getElementById("results_container").removeChild(e))
    
    document.getElementById('assignment_results_modal').style.display='block'

    let selected_class;
    let results;
    for(let i=0; i<classes_list.length; i++){
        let individual_class = classes_list[i];
        if(individual_class.class_name == selected_class_name){
            selected_class = individual_class;
            break;
        }
    }
    let assignments = selected_class.assignments;

    for(let i=0; i<assignments.length; i++){
        let assignment = assignments[i];
        if(assignment.assignment_name == assignment_name){
            results = assignment.scores
            break;
        }
    }
    for(let i=0; i<results.length; i++){
        let result = results[i];
        let name = result.last_name + ", " + result.first_name; 
        
        let results_container = document.getElementById("results_container")
        let result_btn = document.createElement("button");
        let name_text = document.createElement("h3")
        let score_text = document.createElement("h3")

        name_text.id = "results_button_name_text"
        score_text.id = "results_button_score_text"
        name_text.innerHTML = name;
        score_text.innerHTML = result.score;

        result_btn.className = "result_button";
        result_btn.appendChild(name_text);
        result_btn.appendChild(score_text);
        results_container.appendChild(result_btn);

    }
}