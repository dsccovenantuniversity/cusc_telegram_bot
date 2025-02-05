
const fileInput = document.querySelector("#file-js-example input[type=file]");
fileInput.onchange = () => {
    if (fileInput.files.length > 0) {
        const fileName = document.querySelector("#file-js-example .file-name");
        fileName.textContent = fileInput.files[0].name;
    }
};

const md = markdownit();
const textarea = document.querySelector("[name=message]");

textarea.addEventListener(
    "input",
    (e) => {
        const preview = document.querySelector("#preview");
        preview.innerHTML = md.render(e.target.value);
    },
    false
)

function disableOptions(element, optionsToDisable) {
    for (let i = 0; i < element.options.length; i++) {
        if (optionsToDisable.includes(element.options[i].value)) {
            element.options[i].disabled = true;
        } else {
            element.options[i].disabled = false;
        }
    }
}

const levelSelect = document.querySelector("[name=levels]");
const collegeSelect = document.querySelector('[name=colleges]');
levelSelect.addEventListener(
    'click',
    (e) => {
        if (levelSelect.value === "500 Level Students") {
            disableOptions(collegeSelect, ["CMSS Students", "CLDS Students"]);
        }
        else {
            disableOptions(collegeSelect, []);
        }
    }
)

collegeSelect.addEventListener(
    'click',
    (e) => {
        if (collegeSelect.value === "CMSS Students" || collegeSelect.value === "CLDS Students") {
            disableOptions(levelSelect, ["500 Level Students"]);
        }
        else {
            disableOptions(levelSelect, []);
        }
    }
)
