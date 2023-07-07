
const ID_doc = new URLSearchParams(window.location.search).get('id');

let recogitoInstance;
let currentEntityTags = [];
let all_entity_annotations = [];
let all_relation_annotations = [];
let mode_is_Entity = true;


function _deleteRelation(relation) {
    const index = all_relation_annotations.findIndex(item => item.id === relation.id);
    if (index !== -1) {
        all_relation_annotations.splice(index, 1);
    }
}
function _deleteAnnotation(annotation) {
    if(annotation.id[0] !== "#"){
        annotation.id = "#" + annotation.id;
    }
    const index = all_entity_annotations.findIndex(item => item.id === annotation.id);
    if (index !== -1) {
        all_entity_annotations.splice(index, 1);
    }
    all_relation_annotations = all_relation_annotations.filter(item => item.target[0].id !== annotation.id && item.target[1].id !== annotation.id);
    console.log(all_relation_annotations);
}
function _addAnnotation(annotation){
    if(annotation.id[0] !== '#'){
        annotation.id = "#" + annotation.id;
    }
    all_entity_annotations.push(annotation);

}
function _addRelation(relation){
    all_relation_annotations.push(relation);

}
function _updateAnnotation(annotation){
    const index = all_entity_annotations.findIndex(item => item.id === annotation.id);
    all_entity_annotations[index] = annotation;
}
function _updateRelation(relation){
    const index = all_relation_annotations.findIndex(item => item.id === relation.id);
    all_relation_annotations[index] = relation;
}

async function fetchEntityTags() {
    const response = await fetch("entity_tags");
    if (!response.ok) {
        throw new Error(`Failed to fetch data. Status: ${response.status}.`);
    }
    const data = await response.json();
    return data;

}
async function fetchRelationTags() {
    const response = await fetch("relation_tags");
    if (!response.ok) {
        throw new Error(`Failed to fetch data. Status: ${response.status}.`);
    }
    const data = await response.json();
    return data;

}
async function fetch_oneDocument() {
    const response = await fetch("documents/" + ID_doc);
    if (!response.ok) {
        throw new Error(`Failed to fetch data. Status: ${response.status}.`);
    }
    const data = await response.json();
    return data;

}

function initRecogitoInstance(Etags, Rtags) {
    recogitoInstance = Recogito.init({
        content: 'content',
        locale: 'auto',
        widgets: [
            { widget: 'COMMENT' },
            { widget: 'TAG', vocabulary: Etags }
        ],
        relationVocabulary: Rtags
    });


    recogitoInstance.on('createAnnotation',(annotation, overrideId) => {
        const reqBody = { ...annotation };
        reqBody["document_id"] = ID_doc;
        if (mode_is_Entity) {
            fetch('annotations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reqBody)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.detail !== undefined) {
                        recogitoInstance.removeAnnotation(annotation);
                        console.log(data)
                        return;
                    }
                    annotation.id = "#" + data.id;
                    _addAnnotation(annotation);
                    console.log(data)
                    overrideId("#" + data.id);
                    initFilter();
                    updateCounters();
                });
        }
        else {
            parseRelationIDsToDB(reqBody);
            fetch('relations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reqBody)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.detail !== undefined) {
                        console.log(data)
                        //TODO: torolni a created relation-t
                        //  RecogitoJS does NOT support removeAnnotation() for relations
                        return;
                    }
                    console.log(data)
                    parseRelationIDsToClientSide(annotation);
                    annotation.id = data.id;
                    _addRelation(annotation);
                    console.log(all_relation_annotations);
                    overrideId(data.id);
                    initFilter();
                    updateCounters();
                    
                });
        }
    });
    recogitoInstance.on('selectAnnotation', (annotation) => console.log(annotation));

    recogitoInstance.on('updateAnnotation', function (annotation, previous) {
        if (mode_is_Entity) {
            let reqBody = {};
            let comments = [];
            let tags = [];
            for (item of annotation.body) {
                if (item.purpose === "tagging")
                    tags.push(item.value);
                else if (item.purpose === "commenting")
                    comments.push(item.value);
            }
            reqBody["comments"] = comments
            reqBody["tags"] = tags
            fetch('annotations/' + annotation.id.substring(1), {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reqBody)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.detail !== undefined) {
                        console.log(data);
                        recogitoInstance.removeAnnotation(annotation);
                        recogitoInstance.addAnnotation(previous);
                        return;
                    }
                    _updateAnnotation(annotation);
                    console.log(data);
                    initFilter();
                })
                .catch(error => console.log(error))
        }
        else {
            const reqBody = {};
            reqBody["tag"] = annotation.body[0].value;
            fetch('relations/' + annotation.id, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reqBody)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.detail !== undefined) {
                        console.log(data);
                        recogitoInstance.removeAnnotation(annotation);
                        recogitoInstance.addAnnotation(previous);
                        return;
                    }
                    _updateRelation(annotation);
                    initFilter();
                    console.log(data);
                })
                .catch(error => console.log(error))
        }
    });

    recogitoInstance.on('deleteAnnotation', function (annotation) {
        console.log(annotation);
        if (mode_is_Entity) {
            fetch('annotations/' + annotation.id.substring(1), {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                //TODO: ha nem sikerult -> addAnnotation()
                _deleteAnnotation(annotation);
                console.log(data);
                initFilter();
                console.log(all_entity_annotations)
                updateCounters();
            })
            .catch(error => console.log(error))
        }
        else {
            
            fetch('relations/' + annotation.id, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                //TODO: ha nem sikerult -> addAnnotation()
                //RecogitoJS nem tamogatja
                _deleteRelation(annotation);
                console.log(data);
                initFilter();
                updateCounters();
            })
            .catch(error => console.log(error))
        }

    });
}
function load(doc) {
    document.getElementById("title").innerText = doc.title;
    document.getElementById("countE").innerText = doc.annotations.length;
    document.getElementById("countR").innerText = doc.relations.length;
    document.getElementById("content").innerText = doc.content;
}
function filterRecogito(tagName) {
    console.log(tagName)
    filtered_annotations = [];
    for (let ann of all_entity_annotations) {
        for (let i of ann["body"]) {
            if (i["purpose"] == "tagging") {
                if (i["value"] == tagName) {
                    filtered_annotations.push(ann);
                    break;
                }
            }
        }
    }
    filtered_relations = [];
    for(let rel of all_relation_annotations){
        let one = false;
        let two = false;
        for(let a of filtered_annotations){
            if(rel.target[0].id === a.id)
                one = true;
            if(rel.target[1].id === a.id){
                two = true;
            }
        }
        if(one && two){
            filtered_relations.push(rel);
        }
    }
    recogitoInstance.setAnnotations(filtered_annotations.concat(filtered_relations));
    const e = document.getElementById("countE");
    e.innerText = filtered_annotations.length;
    const r = document.getElementById("countR");
    r.innerText = filtered_relations.length;

}
function updateCounters(){
    const e = document.getElementById("countE");
    e.innerText = all_entity_annotations.length;
    const r = document.getElementById("countR");
    r.innerText = all_relation_annotations.length;
}

function updateCurrentTags() {
    let uniqueTags = [];
    for (let item of all_entity_annotations) {
        for (let i of item["body"]) {
            if (i["purpose"] == "tagging") {
                if (!uniqueTags.includes(i["value"])) {
                    uniqueTags.push(i["value"]);
                }
            }
        }
    }
    currentEntityTags = uniqueTags;
}

function initFilter() {
    updateCurrentTags();
    console.log(currentEntityTags);
    const listTags = document.getElementById("filter");
    listTags.innerHTML = "";
    const element = document.createElement("li");
    element.classList.add("dropdown-item");
    element.classList.add("btn");
    element.innerText = "ALL";
    element.addEventListener("click", () => {
        const ALL = all_entity_annotations.concat(all_relation_annotations);
        console.log(ALL);
        recogitoInstance.setAnnotations(ALL);
        const b = document.getElementById("dropdownMenuButton");
        b.innerText = "ALL";
        updateCounters();
    });
    listTags.appendChild(element);

    for (let i = 0; i < currentEntityTags.length; i++) {
        const e = document.createElement("li");
        e.classList.add("dropdown-item");
        e.classList.add("btn");
        e.innerText = currentEntityTags[i];
        e.addEventListener("click", () => {
            filterRecogito(currentEntityTags[i]);
            const b = document.getElementById("dropdownMenuButton");
            b.innerText = currentEntityTags[i];
        });
        listTags.appendChild(e);
    }
}
function initToggleButton() {
    const toggleB = document.getElementById("toggle");
    toggleB.addEventListener("click", async () => {
        console.log(recogitoInstance.getAnnotations());
        if (mode_is_Entity) {
            mode_is_Entity = false;
            recogitoInstance.setMode("RELATIONS");
            toggleB.innerHTML = "Relations";
        }
        else {
            mode_is_Entity = true;
            recogitoInstance.setMode("ANNOTATION");
            toggleB.innerHTML = "Entities";
        }

    });
}

function parseIdsToClientSide(entityArray, relationArray) {
    for (let item of entityArray) {
        item.id = "#" + item.id;
    }
    for (let item of relationArray) {
        item.target[0].id = "#" + item.target[0].id;
        item.target[1].id = "#" + item.target[1].id;
    }
}
function parseAnnIdToDB(annotation) {
    annotation.id = annotation.id.substring(1);
}
function parseAnnToClientSide(annotation) {
    annotation.id = "#" + annotation.id;
}

function parseRelationIDsToDB(annotation) {

    annotation.target[0].id = annotation.target[0].id.substring(1);
    annotation.target[1].id = annotation.target[1].id.substring(1);

}
function parseRelationIDsToClientSide(annotation) {

    annotation.target[0].id = "#" + annotation.target[0].id;
    annotation.target[1].id = "#" + annotation.target[1].id;

}
function initAiButton(){
    const button = document.getElementById("spacy");
    button.addEventListener("click", () => {
        const loadingAnimation = document.getElementById("loading");
        console.log(loadingAnimation.classList);
        loadingAnimation.classList.remove("invisible");
        console.log(loadingAnimation.classList);
        fetch("documents/" + ID_doc +"/spacy-ai", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.detail !== undefined) {
                    console.log(data)
                    return;
                }
                console.log(data)
                data = data.map(obj => {
                    return { ...obj, id: "#" + obj.id };
                  });
                all_entity_annotations = all_entity_annotations.concat(data);
                console.log(all_entity_annotations);
                recogitoInstance.setAnnotations(all_entity_annotations.concat(all_relation_annotations));
                const b = document.getElementById("dropdownMenuButton");
                b.innerText = "ALL"
                initFilter();
                updateCounters();
                document.getElementById("loading").classList.add('invisible');
                
            });
    })
}

async function init() {

    //setting data
    const entity_tags = await fetchEntityTags();
    const relation_tags = await fetchRelationTags();
    const doc = await fetch_oneDocument();
    let entity_annotations = doc.annotations;
    let relation_annotations = doc.relations;
    parseIdsToClientSide(entity_annotations, relation_annotations);
    all_entity_annotations = entity_annotations;
    all_relation_annotations = relation_annotations
    console.log(all_relation_annotations)
    //initializing dom elements
    load(doc);
    initFilter();
    initToggleButton();
    initAiButton();

    //initializing RecogitoJS
    initRecogitoInstance(entity_tags, relation_tags);
    await recogitoInstance.setAnnotations(entity_annotations.concat(relation_annotations));
    const a = recogitoInstance.getAnnotations();
    console.log(a);


}
//entry point of the application
(function () {

    init();

})();