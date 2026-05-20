const happySlider = document.getElementById("happySlider")
const hopefulSlider = document.getElementById("hopefulSlider")
const contentSlider = document.getElementById("contentSlider")
const irritatedSlider = document.getElementById("irritatedSlider")
const anxiousSlider = document.getElementById("anxiousSlider")
const depressedSlider = document.getElementById("depressedSlider")
const submitBtn = document.getElementById("create-btn")
const userId = localStorage.getItem("userId")

submitBtn.addEventListener('click', async () => {
    const happyValue = Number(happySlider.value)
    const hopefulValue = Number(hopefulSlider.value)
    const contentValue = Number(contentSlider.value)
    const irritatedValue = Number(irritatedSlider.value)
    const anxiousValue = Number(anxiousSlider.value)
    const depressedValue = Number(depressedSlider.value)

    const emotionsArr = [
    {
        type: "happy",
        value: Number(happySlider.value)
    },
    {
        type: "hopeful",
        value: Number(hopefulSlider.value)
    },
    {
        type: "content",
        value: Number(contentSlider.value)
    },
    {
        type: "irritated",
        value: Number(irritatedSlider.value)
    },
    {
        type: "anxious",
        value: Number(anxiousSlider.value)
    },
    {
        type: "depressed",
        value: Number(depressedSlider.value)
    }
]
    
    console.log(emotionsArr)
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