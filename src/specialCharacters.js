const specialCharacters = document.querySelector('#special-characters');

const specialCharacterArray = [
    "श", "ष", "स", "व",
    "त", "ट", "ठ", "द",
    "ड", "ध", "ढ", "छ",
    "न", "ण", "ङ", "त्र",
    "द्य", "ञ", "ज", "ज्ञ",
    "ि", "ी", "ु", "ू",
    "े", "ै", "ो", "ौ",
    "्", "ृ", "ं ", "ँ",
    "ा", "ः",
    "ळ", "ॐ", "ङ्ग", "ऋ", "ॠ",
]

for (let i = 0; i < specialCharacterArray.length; i++) {
    let specialCharacter = specialCharacterArray[i];
    let specialCharacterButton = document.createElement("button");
    specialCharacterButton.textContent = specialCharacter;
    specialCharacterButton.addEventListener("click", (function (character) {
        return function () {
            inputField.value += character;
        };
    })(specialCharacter));
    specialCharacters.appendChild(specialCharacterButton);
}
