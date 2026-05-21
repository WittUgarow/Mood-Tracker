const entryTitleElem = document.querySelector(".entry-header")
const entryNumElem = entryTitleElem.querySelector("h2")
const dateElem = entryTitleElem.querySelector("p")
const emotionsDiv = document.querySelector(".emotions")

async function init(){
    const params = new URLSearchParams(window.location.search)
    const entryId = params.get("id")
    const response = await fetch(`http://127.0.0.1:8000/entries/${entryId}`)
    const result = await response.json()
    const entry = result[0]
    fillEntry(entry.id, new Date(entry.created_at), entry.emotions)
}

function fillEntry(entryId, date, emotions){
    entryNumElem.innerHTML = `Entry #${entryId}`
    const formattedDate = 
    `${date.toDateString()} - ${
        date.toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit"
        })
    }`
    dateElem.innerHTML = formattedDate

    for (let i = 0; i<emotions.length; i++){
        const emotionBar = `<div class="emotion-row">
          <span class="label">${emotions[i].type}</span>
          <span class="value">${emotions[i].value}</span>
          <div class="bar"><div class="fill" style="width:${emotions[i].value}%"></div></div>
        </div>`
        emotionsDiv.innerHTML += emotionBar
    }

    console.log(emotions)
}

init()