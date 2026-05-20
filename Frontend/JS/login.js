const nameInput = document.getElementById("nameInput");
const passwordInput = document.getElementById("passwordInput");
const loginBtn = document.getElementById("loginBtn");

loginBtn.addEventListener('click', async function(){
    let name = nameInput.value;
    let password = passwordInput.value;
    let result = await attemptLogin(name, password)
    console.log(result)
    if (result.status){
        localStorage.setItem("name", name);
        localStorage.setItem("password", password);
        localStorage.setItem("userId", result.userId)
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
    return data;
}