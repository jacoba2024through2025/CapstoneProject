const minusBtn = document.getElementById("minus-btn");
const plusBtn = document.getElementById("add-btn");
const quantityInput = document.getElementById("quantity");
const formQuantity = document.getElementById("form-quantity");

plusBtn.addEventListener("click", (e) => {
  quantityInput.value = parseInt(quantityInput.value) + 1;
  formQuantity.value = quantityInput.value;
  console.log(quantityInput.value);
  console.log(formQuantity.value);
});

minusBtn.addEventListener("click", (e) => {
  if (parseInt(quantityInput.value) > 1) {
    quantityInput.value = parseInt(quantityInput.value) - 1;
    formQuantity.value = quantityInput.value;
    console.log(quantityInput.value);
    console.log(formQuantity.value);
  }
});

// const quantityContainer = document.querySelector(".quantity_selector");
// const minusBtn = quantityContainer.querySelector(".minusBtn")
// const plusBtn = quantityContainer.querySelector(".addBtn")
// const inputBox = quantityContainer.querySelector(".input-box");

// function updateButtonStatus() {
//     const value = parseInt(inputBox.value);
//     minusBtn.disabled = value <= 1;
//     plusBtn.disabled = value >= parseInt(inputBox.max);
// }

// function handleQuantityChange() {
//     let value = parseInt(inputBox.value);
//     value = isNan(value) ? 1 : value;
// }

// function handleInputChange(event) {
//     if (event.target.classList.contains("minusBtn")) {

//     }
// }

// function decreaseValue() {
//     let value = parseInt(inputBox.value);
//     value = isNaN(value) ? 1 : Math.max(-1, 1)
//     inputBox.value = value;
//     updateButtonStatus();
// }

// function increaseValue() {
//     let value = parseInt(inputBox.value);
//     value = isNaN(value) ? 1 : Math.min(value + 1, parseInt(inputBox.max));
//     inputBox.value = value;
//     updateButtonStatus();
// }
