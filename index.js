const inputField = document.getElementById("transliterateTextarea");
const suggestionDiv = document.getElementById("suggestions");
const selectFolderButton = document.getElementById("selectFolderButton");
const imageViewer = document.getElementById("imageViewer");
const image = document.getElementById("image");
const prevButton = document.getElementById("prevButton");
const nextButton = document.getElementById("nextButton");
const deleteButton = document.getElementById("deleteButton");
const saveButton = document.getElementById("saveButton");
const toggleNepaliSwitch = document.getElementById("toggleNepaliSwitch");
const currentIndex = document.querySelector(".current-index");

let suggestions = [];
let suggestedWord = "";
let images = [];
let imgDir = "";
let currentImageIndex = 265;
let csvPath = "";
let csvData = null;
let isDirty = false;
let nepaliMode = true;

const selectSuggestedWord = (wordList, suggestedWord) => {
  wordList[wordList.length - 1] = suggestedWord;
  inputField.value = wordList.join(" ") + " ";
  suggestionDiv.innerHTML = "";
  inputField.focus();
  isDirty = false;
};

const updateImage = () => {
  if (csvData !== null) {
    if (currentImageIndex >= 0 && currentImageIndex <= csvData.length - 1) {
      image.src =
        imgDir + "/" + csvData[currentImageIndex].image.replaceAll("#", "%23");

      inputField.value = csvData[currentImageIndex].text;
      toggleNepaliSwitch.checked = csvData[currentImageIndex].isNepali;
      // nepaliMode = csvData[currentImageIndex].isNepali;
      nepaliMode = true
      
      isDirty = false;
      currentIndex.textContent = currentImageIndex + 1
    }
  }
};

const updateRow = () => {
  if (csvData !== null) {
    const text = inputField.value;
    csvData[currentImageIndex].text = text.trim();
    csvData[currentImageIndex].isNepali = true;
  }
};

const toggleNepaliMode = (isNepaliMode) => {
  nepaliMode = isNepaliMode;
};

inputField.addEventListener("input", async (e) => {
  const text = inputField.value;
  let wordList = text.trim().split(" ");
  const lastWord = wordList[wordList.length - 1];

  if (!nepaliMode) {
    return;
  }

  if (e.data === " ") {
    if (isDirty) {
      selectSuggestedWord(wordList, suggestedWord);
      suggestionDiv.innerHTML = "";
    }
    return;
  }

  isDirty = true;
  fetch(
    `https://inputtools.google.com/request?text=${lastWord}&itc=ne-t-i0-und&num=10&ie=utf-8&oe=utf-8`
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
          selectSuggestedWord(wordList, suggestion, true);
        });
        suggestionDiv.appendChild(suggestionButton);
      });
    });
});

selectFolderButton.addEventListener("click", async (e) => {
  window.myAPI.selectFolder().then(({ folderPath, imageList }) => {
    imgDir = folderPath;
    csvPath = imgDir + "/nic_train_alphabet.csv";
    images = imageList;
    console.log(folderPath, imageList);
    d3.csv(csvPath)
      .then((csv) => {
        csvData = csv;
        updateImage();
      })
      .catch((err) => {
        console.log(err);
        csvData = [];
        images.forEach((image) => {
          csvData.push({ image: image, text: "", isNepali: false });
        });
        updateImage();
      });
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
  window.myAPI.saveCSV(csvPath, csvData);
});

deleteButton.addEventListener("click", async (e) => {
  window.myAPI
    .deleteImage(imgDir + "/" + csvData[currentImageIndex].image)
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
