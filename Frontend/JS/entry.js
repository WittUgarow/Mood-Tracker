const defaultEmotions = ["happy", "hopeful", "content", "irritated", "anxious", "depressed"]
const emotionsPanel = document.querySelector(".emotions")


// const happySlider = document.getElementById("happySlider")
// const hopefulSlider = document.getElementById("hopefulSlider")
// const contentSlider = document.getElementById("contentSlider")
// const irritatedSlider = document.getElementById("irritatedSlider")
// const anxiousSlider = document.getElementById("anxiousSlider")
// const depressedSlider = document.getElementById("depressedSlider")
const submitBtn = document.getElementById("create-btn")
const userId = localStorage.getItem("userId")

init()


function init(){
    for (let i = 0; i< defaultEmotions.length; i++){
        createSlider(defaultEmotions[i])
    }
}

function createSlider(emotion){
    const slider = `
            <div class="emotion-slider">
                <label>${emotion}</label>
                <input type="range" min="0" max="100" value="0" id="${emotion}Slider">
            </div>`
    emotionsPanel.innerHTML += slider
}


submitBtn.addEventListener('click', async () => {
    let emotionsArr = []
    const sliders = document.querySelectorAll(".emotion-slider")
    for (let i = 0; i<sliders.length; i++){
        const emotion = sliders[i].querySelector("label").innerHTML
        const value = sliders[i].querySelector("input").value
        emotionsArr.push({"type": emotion, "value": value})
    }

    console.log(emotionsArr )
    const response = await fetch("http://127.0.0.1:8000/entries", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: userId,
            emotions: emotionsArr 
        })
        })
    window.location.assign("main.html");
})