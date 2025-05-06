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

