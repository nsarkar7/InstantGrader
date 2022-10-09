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

function get_classes() {
    let teacher_id = sessionStorage.getItem("id");

    get_classes_request = new XMLHttpRequest();

    get_classes_request.onreadystatechange = function() {
        if (this.status == 200 && this.readyState == 4) {
            let classes = JSON.parse(this.responseText);
            for(let i=0; i<classes.length; i++){
                let individual_class = classes[i];
                let sidebar = document.getElementById("sidebar");
                let class_btn = document.createElement("button");
                class_btn.innerHTML = individual_class.class_name;
                class_btn.className = "class_button";
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