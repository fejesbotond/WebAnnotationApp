let isUploadTried = false;

async function fetchList() {
    try {
        const response = await fetch("documents");
        if (!response.ok) {
            throw new Error(`Failed to fetch data. Status: ${response.status}.`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        throw error;
    }
}
function setModalOnCLoseListener() {
    const modal = document.getElementById("modalId");
    modal.addEventListener("hidden.bs.modal", () => {
        if (!isUploadTried) {
            return;
        }
        deleteAlertModalDOM();
        isUploadTried = false;
    })
}
function deleteAlertModalDOM() {
    const alertDOM = document.getElementById("uploadMessage");
    alertDOM.innerHTML = '';
}
function addElementToTable(tableDOM, data) {

    function parseDate(date) {
        function zero(number) {
            if (number < 10) {
                return "0" + number;
            }
            return number.toString();
        }
        const dateObj = new Date(date);
        const year = dateObj.getFullYear();
        const month = zero(dateObj.getMonth() + 1);
        const day = zero(dateObj.getDate());
        const hour = zero(dateObj.getHours());
        const min = zero(dateObj.getMinutes());
        return `${year}.${month}.${day}. ${hour}:${min}`;
    }

    const tableRowDOM = document.createElement('tr');
    const cellDOM0 = document.createElement('td');
    const cellDOM1 = document.createElement('td');
    const cellDOM2 = document.createElement('td');
    const cellDOM3 = document.createElement('td');
    const cellDOM4 = document.createElement('td');
    const cellDOM5 = document.createElement('td');
    const buttonTrashDOM = document.createElement('button');
    const buttonLink = document.createElement('button');

    tableRowDOM.setAttribute('id', data.id);
    cellDOM1.innerHTML = data.title;
    cellDOM2.innerHTML = data.file_name;
    cellDOM3.innerHTML = data.count_annotations;
    cellDOM4.innerHTML = parseDate(data.date);
    buttonTrashDOM.classList.add('btn');
    buttonTrashDOM.classList.add('btn-danger');
    buttonTrashDOM.innerHTML = '<i class="far fa-trash-alt"></i>';
    buttonTrashDOM.addEventListener("click", async () => {
        const requestObj = {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        }
        const response = await fetch("documents/" + data.id, requestObj);
        if (!response.ok) {
            console.log("delete failed");
            return;
        }
        console.log("successful delete");
        const rowDOM = document.getElementById(data.id);
        rowDOM.remove();

    });
    buttonLink.classList.add('btn');
    buttonLink.classList.add('btn-primary');
    buttonLink.innerHTML = '<i class="fas fa-external-link-alt"></i>';
    buttonLink.addEventListener("click", function(){
        console.log("asd");
        window.location.href = `/document?id=${data.id}`;
        console.log(window.location.href);
    });
    cellDOM5.appendChild(buttonTrashDOM);
    cellDOM0.appendChild(buttonLink);
    tableRowDOM.appendChild(cellDOM0);
    tableRowDOM.appendChild(cellDOM1);
    tableRowDOM.appendChild(cellDOM2);
    tableRowDOM.appendChild(cellDOM3);
    tableRowDOM.appendChild(cellDOM4);
    tableRowDOM.appendChild(cellDOM5);
    tableDOM.appendChild(tableRowDOM);
}

function setSubmitListener() {
    const submitButton = document.getElementById("submitButton");
    submitButton.addEventListener("click", async (event) => {
        event.preventDefault();

        deleteAlertModalDOM();

        const formData = new FormData(document.getElementById("form"));

        const response = await fetch('documents', { method: "POST", body: formData });
        isUploadTried = true;
        if (!response.ok) {
            const failDOM = document.createElement('div');
            failDOM.classList.add("alert");
            failDOM.classList.add("alert-danger");
            failDOM.innerHTML = "Failed uploading.";
            document.getElementById("uploadMessage").appendChild(failDOM);
            return;
        }
        const data = await response.json();
        addElementToTable(document.getElementById("table"), data);

        let myModal = bootstrap.Modal.getInstance((document.getElementById('modalId')));
        myModal.hide();

    });
}

function renderList(data) {
    const tableDOM = document.getElementById('table');
    tableDOM.innerHTML = '';
    for (let i = 0; i < data.length; i++) {
        addElementToTable(tableDOM, data[i]);
    }
}
async function initList() {
    const dataList = await fetchList();
    renderList(dataList);

}

(function run() {
    initList();
    setSubmitListener();
    setModalOnCLoseListener();
})();