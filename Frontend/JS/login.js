const nameInput = document.getElementById("nameInput");
const passwordInput = document.getElementById("passwordInput");
const loginBtn = document.getElementById("loginBtn");

loginBtn.addEventListener('click', function(){
    let name = nameInput.value;
    let password = passwordInput.value;
    if (attemptLogin(name, password)){
        localStorage.setItem("name", name);
        localStorage.setItem("password", password);
        window.location.assign("main.html");
    }
})

async function attemptLogin(usernameIn, passwordIn){
    const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: usernameIn,
            password: passwordIn
        })
        })
    const data = await response.json();
    console.log(data.status);
    return data.status;
}