const minusBtn = document.getElementById("minus-btn")
const plusBtn = document.getElementById("add-btn")
const quantityInput = document.getElementById("quantity")
const formQuantity = document.getElementById("form-quantity")

plusBtn.addEventListener("click", (e) => {
    console.log(quantityInput)
    quantityInput.innerText = parseInt(quantityInput.innerText) + 1
    formQuantity.value = quantityInput.innerText
})

minusBtn.addEventListener("click", (e) => {
    if (parseInt(quantityInput.innerText) > 1) {
        quantityInput.innerText = parseInt(quantityInput.innerText) - 1
        formQuantity.value = quantityInput.innerText;
    }
})