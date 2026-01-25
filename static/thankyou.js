
// 取得網址上的 ?number=xxxx
const params = new URLSearchParams(window.location.search);
const orderNumber = params.get("number");






document.addEventListener("DOMContentLoaded", () => {
  initBookingPage();
});



async function initBookingPage() {
  const token = localStorage.getItem("token"); // ← 如果你不是用 token 當 key，改這裡
  if (!token) {
    // 沒 token，直接當未登入
    window.location.href = "/";
    return;
  }

  // 1) 先檢查登入狀態（以 /api/user/auth 為準）
  const user = await fetchUser(token);
  const userNameEl = document.getElementById("userName");
  if (userNameEl) userNameEl.textContent = user.name || "會員";

  // 找到畫面上的 span
  const orderNumberEl = document.getElementById("orderNumber");
  // 顯示
  if (orderNumber && orderNumberEl) {
    orderNumberEl.textContent = orderNumber;
  } else {
    orderNumberEl.textContent = "無法取得訂單編號";

  const user = await fetchUser(token);
  const userNameEl = document.getElementById("userName");
  if (userNameEl) userNameEl.textContent = user.name || "會員";
}


}

async function fetchUser(token) {
  try {
    const res = await fetch("/api/user/auth", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!res.ok) return null;

    const data = await res.json();
    // 你的 user API 回傳結構通常是 { data: {...} } 或 { data: null }
    if (!data || !data.data) return null;

    return data.data; // user object
  } catch (err) {
    console.error("fetchUser error:", err);
    return null;
  }
}