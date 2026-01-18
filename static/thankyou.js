
// 取得網址上的 ?number=xxxx
const params = new URLSearchParams(window.location.search);
const orderNumber = params.get("number");

// 找到畫面上的 span
const orderNumberEl = document.getElementById("orderNumber");

// 顯示
if (orderNumber && orderNumberEl) {
  orderNumberEl.textContent = orderNumber;
} else {
  orderNumberEl.textContent = "無法取得訂單編號";
}