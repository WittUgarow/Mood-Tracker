    const entriesDiv = document.getElementById("entryDiv")
const userId = localStorage.getItem("userId")
 
getEntries(userId).then((data) => {insertEntries(data)})

async function getEntries(userId) {
    const response = await fetch(`http://127.0.0.1:8000/entries?userId=${userId}`);
    const data = await response.json();
    return data;
}

function insertEntries(entries){
    console.log(entries)
    for (let i = 0; i<entries.length; i++) {
        const id = entries[i].id
        const date = new Date(entries[i].created_at)
        const emotions = entries[i].emotions
        createEntryElement(id, date, emotions);
    }
}

function createEntryElement(number, date, emotions){
    const formattedDate = 
    `${date.toDateString()} - ${
        date.toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit"
        })
    }`
    entriesDiv.innerHTML += `
        <div class="entry card" id="entry${number}">
            <h3>Entry #${number}</h3>
            <div class="entry-meta">${formattedDate} </div>
            <div class="emotions">
            </div>
        </div>`

    const entryEmotions = document.querySelector(`#entry${number} .emotions`)
    for (let i = 0; i<emotions.length; i++){
        entryEmotions.innerHTML += `<span>${emotions[i].type}: ${emotions[i].value}</span>`
    }
}