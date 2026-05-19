const entriesDiv = document.getElementById("entryDiv")

getEntries(1).then((data) => {insertEntries(data)})

async function getEntries(userId) {
    const response = await fetch(`http://127.0.0.1:8000/entries?userId=${userId}`);
    const data = await response.json();
    return data;
}

function insertEntries(entries){
    for (const id in entries) {
        const entry = entries[id];
        createEntryElement(id, new Date(entry.created_at), entry.emotions);
    }
}

function createEntryElement(number, date, emotions){
    console.log("Ran")
    entriesDiv.innerHTML += `
        <div class="entry card" id="entry${number}">
            <h3>Entry #${number}</h3>
            <div class="entry-meta">${date.toDateString()}</div>
            <div class="emotions">
            </div>
        </div>`

    const entryEmotions = document.querySelector(`#entry${number} .emotions`)
    for (let i = 0; i<emotions.length; i++){
        entryEmotions.innerHTML += `<span>${emotions[i].emotion}: ${emotions[i].emotion_value}</span>`
    }
}