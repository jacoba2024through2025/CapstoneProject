// import Stripe from "https://js.stripe.com/v3/";

let ripe = null;
var sessionId = null;

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
fetch("/checkout/")
    .then((result) => {
      return result.json();
    })
    .then((data) => {
      console.log("here", data);
      // Redirect to Stripe Checkout
      sessionId = data.sessionId;
      console.log("sessionId", sessionId);
    })
    .then((res) => {
      console.log(res);
    });
console.log("ripe", ripe);
document.querySelector("#checkout-button").addEventListener("click", () => {
  // Get Checkout Session ID
  console.log("clicked");
  return ripe.redirectToCheckout({ sessionId: sessionId });
});
