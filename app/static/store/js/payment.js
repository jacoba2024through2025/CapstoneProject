// import Stripe from "https://js.stripe.com/v3/";

let ripe = null;

fetch("/config/")
  .then((result) => {
    console.log("result", result);
    return result.json();
  })
  .then((data) => {
    // Initialize Stripe.js
    console.log("successfully got", data);
    ripe = Stripe(data.publicKey);
  });
console.log("ripe", ripe);
document.querySelector("#checkout-button").addEventListener("click", () => {
  // Get Checkout Session ID
  console.log("clicked");
  fetch("/checkout/")
    .then((result) => {
      return result.json();
    })
    .then((data) => {
      console.log("here", data);
      // Redirect to Stripe Checkout
      return ripe.redirectToCheckout({ sessionId: data.sessionId });
    })
    .then((res) => {
      console.log(res);
    });
});
