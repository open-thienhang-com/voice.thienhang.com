let loader, errorMessage;

function showLoading() {
    loader.style.display = 'inline-block';
    errorMessage.style.display = 'none';
}

function hideLoading() {
    loader.style.display = 'none';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showError(message) {
    errorMessage.style.display = 'inline-block';
    errorMessage.innerText = message;
    loader.style.display = 'none';
}

const baseURL = ``;
const modelConfig = {};

const speakerFiles = {};

let allModels = [];

async function loadModelInfo() {
    let modelLanguages, modelSpeakers;
    {
    const response = await fetch(`/models/languages`);
    if(response.ok) {
        modelLanguages = await response.json();
    }
    }
    {
    const response = await fetch(`/models/speakers`);
    if(response.ok) {
        modelSpeakers = await response.json();
    }
    }
    for(const [name, languages] of Object.entries(modelLanguages)) {
    if(!modelConfig[name]) {
        modelConfig[name] = { name };
    }
    modelConfig[name].languages = languages;
    }
    for(const [name, speakers] of Object.entries(modelSpeakers)) {
    if(!modelConfig[name]) {
        modelConfig[name] = { name };
    }
    modelConfig[name].speakers = speakers;
    }
    // console.log(modelLanguages);
    // console.log(modelSpeakers);
    console.log(modelConfig);
    // sort
}

async function loadAllModelsList() {
    const response = await fetch(`/models/all`);
    if(response.ok) {
    allModels = await response.json();
    }
}

function selectSpeaker(event) {
    const fileSelector = document.querySelector('#speaker-file-selector')
    fileSelector.click();
}

async function speakerFileSelected(event) {
    speakerFile = event.target.files[0];
    // const status = document.querySelector('#status')
    // reset file selector: https://stackoverflow.com/a/35323290
    event.target.value = ''
    if(!/safari/i.test(navigator.userAgent)){
    event.target.type = ''
    event.target.type = 'file'
    }

    if(!speakerFile) {
    return;
    }

    console.log('speaker file:', speakerFile);

    addExternalSpeaker(speakerFile);
}

async function clear() {
    const result = document.querySelector(`div#results`);
    result.innerHTML = '';
    document.querySelector(`#results-title`).style.display = 'none';
}

async function generate() {
    const modelName = document.querySelector(`select#model`).value;
    const text = document.querySelector(`textarea#text`).value;
    const language = document.querySelector(`select#language`).value;
    const speaker = document.querySelector(`select#speaker`).value;
    console.log(modelName, language, speaker);
    console.log(text);

    const headers = { 'Accept': 'audio/*' };
    const params = new URLSearchParams();
    params.append('text', text);
    params.append('language', language);

    if (speaker.startsWith('--')) {
        params.append('speaker_wav', speakerFiles[speaker]);
    } else {
        params.append('speaker', speaker);
    }

    // formData.append('download', 'on');
    try {
    showLoading();

    const response = await fetch(`/models/${modelName}/generate?${params.toString()}`, { method: 'GET', headers });
    if(!response.ok) {
        console.log(response);
        // const data = await response.json();
        // data.detail
        showError(`Response ${response.status}: ${response.statusText}`);
        hideLoading();
        return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);


    const result = document.querySelector(`div#results`);
    // result.innerHTML = '';

    const container = document.createElement('div');

    container.classList.add('result');

    const infoContainer = document.createElement('div');

    const now = new Date();
    const nowstring = now.toISOString();
    const datetime = nowstring.replace('T', ' ').replace('Z', ' UTC');
    const speakerName = speaker.startsWith('--') ? speakerFiles[speaker].name : speaker || 'none';

    const info = { 'Date-Time': datetime, Model: modelName, Language: language, Speaker: speakerName, Text: text };
    for(const [title, value] of Object.entries(info)) {
        const div = document.createElement('div');

        const titleSpan = document.createElement('span');
        titleSpan.classList.add('info-title');
        titleSpan.innerText = `${title}: `;
        div.appendChild(titleSpan);

        const valueSpan = document.createElement('span');
        valueSpan.classList.add('info-value');
        valueSpan.innerText = value;
        div.appendChild(valueSpan);

        infoContainer.appendChild(div);
    }

    container.appendChild(infoContainer);

    closeButton = document.createElement('div');
    closeButton.classList.add('close');
    closeButton.innerText = '✗';
    // closeButton.innerHTML = '&Cross;';
    closeButton.title = 'Close Result';
    closeButton.addEventListener('click', e => {
        e.target.parentNode.remove();
        if(document.querySelector(`div#results`).children.length == 0) {
        document.querySelector(`#results-title`).style.display = 'none';
        }
    });
    container.appendChild(closeButton);

    const link = document.createElement('a');
    link.href = url;
    link.innerText = 'Download Wave';
    link.target = '_blank';
    link.download = `output-${nowstring.replaceAll('-', '').replace('T', '-').replaceAll(':', '').substr(0,15)}.wav`;
    container.appendChild(link);


    const videoDiv = document.createElement('div');
    videoDiv.classList.add('video');

    const video = document.createElement('video');
    video.src = url;
    video.controls = true;

    videoDiv.appendChild(video);
    container.appendChild(videoDiv);

    document.querySelector(`#results-title`).style.display = 'block';

    // result.appendChild(container);
    result.insertBefore(container, result.firstChild);

    hideLoading();

    } catch(e) {
    console.error('TTS failed:', e);
    showError(`${e.name}: ${e.message}`);
    hideLoading();
    return;
    }
}

function populateModelSelector() {
    const select = document.querySelector(`select#model`);
    for(const [name, config] of Object.entries(modelConfig)) {
    option = document.createElement('option');
    option.value = name;
    const p = name.split('--');
    option.innerText = [p[0], p[1], p.slice(2).join('--')].join('/') + (config.languages && config.languages.length > 1 ? ` [${config.languages.join(', ')}]` : '');
    select.appendChild(option);
    }
    modelChanged();
}

function populateDownloadModelSelector() {
    const select = document.querySelector(`select#model-to-download`);
    for(const model of allModels) {
    option = document.createElement('option');
    option.value = model;
    const p = model.split('--');
    option.innerText = [p[0], p[1], p.slice(2).join('--')].join('/');
    select.appendChild(option);
    }
}

function addExternalSpeaker(file) {
    const speakerSelect = document.querySelector(`select#speaker`);
    const externalSpeakers = document.querySelector(`select#speaker > optgroup#external-speakers`);
    option = document.createElement('option');
    option.value = '--' + Object.keys(speakerFiles).length;
    option.innerText = file.name;
    speakerFiles[option.value] = file;
    externalSpeakers.appendChild(option);
    speakerSelect.value = option.value;
}

function downloadModelChanged() {
    const modelName = document.querySelector(`select#model-to-download`).value;
    const a = document.querySelector(`a#download-model`);
    a.href = `/models/${modelName}/download`;
    a.classList.remove('hidden');
}

function modelChanged() {
    const modelName = document.querySelector(`select#model`).value;
    const config = modelConfig[modelName];
    // languages
    const languageSelect = document.querySelector(`select#language`);
    languageSelect.innerHTML = '';
    console.log('model changed', modelName, 'config', config);
    for(const language of config.languages) {
    option = document.createElement('option');
    option.value = language;
    option.innerText = language;
    languageSelect.appendChild(option);
    }
    // speakers
    const modelSpeakers = document.querySelector(`select#speaker > optgroup#model-speakers`);
    modelSpeakers.innerHTML = '';
    for(const speaker of config.speakers) {
    option = document.createElement('option');
    option.value = speaker;
    option.innerText = speaker;
    modelSpeakers.appendChild(option);
    }
    if(!config.speakers || config.speakers.length === 0) {
    option = document.createElement('option');
    option.value = '';
    option.innerText = 'default';
    modelSpeakers.appendChild(option);
    }
}

document.addEventListener('DOMContentLoaded', async () => {

    await loadModelInfo();
    await loadAllModelsList();

    loader = document.querySelector('#loader');
    errorMessage = document.querySelector('#error');

    document.querySelector('select#model').addEventListener('change', modelChanged);
    document.querySelector('select#model-to-download').addEventListener('change', downloadModelChanged);
    document.querySelector('button#generate').addEventListener('click', generate);
    document.querySelector('button#clear').addEventListener('click', clear);
    document.querySelector('input#speaker-file-selector').addEventListener('change', speakerFileSelected);
    document.querySelector('#select-speaker').addEventListener('click', selectSpeaker);

    const shiftEnterGenerate = e => {
    if(e.shiftKey && e.keyCode == 13) {
        e.preventDefault();
        e.stopPropagation();
        generate();
    }
    };

    document.querySelector('textarea#text').addEventListener('keydown', shiftEnterGenerate);
    document.querySelector('select#speaker').addEventListener('keydown', shiftEnterGenerate);
    document.querySelector('select#language').addEventListener('keydown', shiftEnterGenerate);
    document.querySelector('select#model').addEventListener('keydown', shiftEnterGenerate);

    populateModelSelector();
    populateDownloadModelSelector();
});