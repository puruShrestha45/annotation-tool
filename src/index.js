const inputField = document.getElementById("transliterateTextarea");
const suggestionDiv = document.getElementById("suggestions");
const selectFolderButton = document.getElementById("selectFolderButton");
const imageContainer = document.querySelector(".image-container");
const image = document.getElementById("image");
const imageCaption = document.getElementById("image-caption");
const prevButton = document.getElementById("prevButton");
const nextButton = document.getElementById("nextButton");
const deleteButton = document.getElementById("deleteButton");
const saveButton = document.getElementById("saveButton");
const toggleNepaliSwitch = document.getElementById("toggleNepaliSwitch");
const currentIndex = document.querySelector("#current-index");
const folderNameSpan = document.querySelector(".folder-name");
const isInvalidCheckbox = document.querySelector("#invalid-image");

let suggestions = [];
let suggestedWord = "";
let images = [];
let imgDir = "";
let formId = "";
let currentImageIndex = 0;
let pathToCsv = "";
let csvData = null;
let nepaliMode = false;
let isInvalid = false;

const selectSuggestedWord = (text, index) => {
  inputField.value = text;
  suggestionDiv.innerHTML = "";
  inputField.focus();
  inputField.setSelectionRange(index, index);
};

const updateImage = () => {
  const imagePath =
    imgDir + "/" + csvData[currentImageIndex].image.replaceAll("#", "%23");
  if (csvData !== null) {
    if (currentImageIndex >= 0 && currentImageIndex <= csvData.length - 1) {
      if (!myAPI.checkFileExists(imagePath)) {
      }

      image.src = imagePath;
      let text = csvData[currentImageIndex].text ?? ""
      if (text == null) {
        text = ""
      }
      // text = String(text);
      console.log(typeof text);
      imageCaption.textContent = formId + "/" + csvData[currentImageIndex].image;
      inputField.value = text.trim();
      isInvalidCheckbox.checked = csvData[currentImageIndex].isInvalid;
      currentIndex.innerHTML = currentImageIndex +1;

      window.myAPI.saveCSV(pathToCsv, csvData);

    }
  }
};

const updateRow = () => {
  if (csvData !== null) {
    const text = inputField.value;
    csvData[currentImageIndex].text =  String(text.trim())  ;
    csvData[currentImageIndex].isNepali = nepaliMode;
    csvData[currentImageIndex].isInvalid = isInvalidCheckbox.checked;
  }
};

const toggleNepaliMode = (isNepaliMode) => {
  nepaliMode = isNepaliMode;
};

inputField.addEventListener("input", async (event) => {
  if (!nepaliMode) {
    return;
  }

  const value = event.target.value;
  const selectionIndex = event.target.selectionStart;

  const wordList = value.trim().replace(/\s+/g, " ").split(" ");

  if (wordList.length == 1 && wordList[0] == "") {
    return;
  }

  let wordIndex = -1;
  let charCount = 0;

  console.log(selectionIndex, "selectionIndex");

  for (let i = 0; i < wordList.length; i++) {
    charCount += wordList[i].length + 1; // Add 1 for the space character
    console.log(wordList[i].length, charCount);

    if (charCount >= selectionIndex) {
      wordIndex = i;
      break;
    }
  }
  console.log(wordIndex, "wordIndex");

  wordIndex = wordIndex == -1 ? wordList.length - 1 : wordIndex;

  console.log(wordList, "wordList");
  console.log(wordIndex, "wordIndex");

  const selectedWord = wordList[wordIndex];

  fetch(
    `https://inputtools.google.com/request?text=${selectedWord}&itc=ne-t-i0-und&num=10&ie=utf-8&oe=utf-8`
  )
    .then((response) => response.json())
    .then((data) => {
      suggestions = data[1][0][1];
      suggestedWord = suggestions[0];
      suggestionDiv.innerHTML = "";

      suggestions.forEach((suggestion) => {
        let suggestionButton = document.createElement("button");
        suggestionButton.textContent = suggestion;
        suggestionButton.addEventListener("click", () => {
          wordList[wordIndex] = suggestion;
          const finalText = wordList.join(" ") + " ";
          const selectedWordIndex =
          finalText.indexOf(suggestedWord) + suggestedWord.length + 1;
          selectSuggestedWord(finalText, selectedWordIndex);
          suggestionDiv.innerHTML = "";
          // selectSuggestedWord(wordList, suggestion, true);
        });
        suggestionDiv.appendChild(suggestionButton);
      });

      console.log(event, "event.key");
      if (event.data == " " && value[selectionIndex - 2] != " ") {
        console.log("space pressed", suggestedWord);
        wordList[wordIndex] = suggestedWord;
        const finalText = wordList.join(" ") + " ";
        const selectedWordIndex =
          finalText.indexOf(suggestedWord) + suggestedWord.length + 1;
        selectSuggestedWord(finalText, selectedWordIndex);
        suggestionDiv.innerHTML = "";
      }
    });
});

selectFolderButton.addEventListener("click", async (e) => {
  console.log("selectFolderButton clicked");
  window.myAPI
    .selectFolder()
    .then(({ folderPath, folderName, imageList, loadedCSVData, csvPath }) => {
      imgDir = folderPath;
      images = imageList;
      pathToCsv = csvPath;
      formId = folderName;

      folderNameSpan.textContent =' Folder: ' + folderName;
      currentImageIndex = 0;
      csvData = loadedCSVData;

      updateImage();
      imageContainer.style.minHeight = "90px";
    })
    .catch((err) => {
      console.log(err);
      console.log("folder not selected");
    });
});

prevButton.addEventListener("click", async (e) => {
  if (currentImageIndex > 0) {
    updateRow();
    currentImageIndex--;
    updateImage();
  }
});

nextButton.addEventListener("click", async (e) => {
  if (currentImageIndex < csvData.length - 1) {
    updateRow();
    currentImageIndex++;
    updateImage();
  }
});

saveButton.addEventListener("click", async (e) => {
  updateRow();
  window.myAPI.saveCSV(pathToCsv, csvData);
});

deleteButton.addEventListener("click", async (e) => {
  console.log(imgDir);
  
  window.myAPI
    .deleteImage(imgDir, csvData[currentImageIndex].image)
    .then(() => {
      csvData.splice(currentImageIndex, 1);
      if (currentImageIndex >= csvData.length) {
        currentImageIndex = csvData.length - 1;
      }
      updateImage();
    })
    .catch((err) => {
      console.log(err);
    });
});

toggleNepaliSwitch.addEventListener("click", (e) => {
  toggleNepaliMode(e.target.checked);
  console.log(e.target.checked);
});

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight" && e.ctrlKey && e.shiftKey) {
    nextButton.click();
  } else if (e.key === "ArrowLeft" && e.ctrlKey && e.shiftKey) {
    prevButton.click();
    // } else if (e.key === "Delete") {
    //   deleteButton.click();
  } else if (e.key === "s" && e.ctrlKey) {
    saveButton.click();
  } else if (e.key === "o" && e.ctrlKey) {
    selectFolderButton.click();
  } else if (e.key === "t" && e.ctrlKey) {
    toggleNepaliSwitch.click();
  }
});
