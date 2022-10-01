
function handleCredentialResponse(response){
    let xhr = new XMLHttpRequest();
    let str = response.credential;
    let reqUrl = "/verify?str=" + str; 
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let user_data = JSON.parse(this.responseText);
            sessionStorage.setItem('name', user_data.name);
            sessionStorage.setItem('email', user_data.email);
            sessionStorage.setItem('name', user_data.name);
            window.location.replace("/app");
        }
    }    
    xhr.open("GET", reqUrl);
    xhr.send();
}

