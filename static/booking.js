document.addEventListener("DOMContentLoaded", () => {
  initBookingPage();
});

function formatTimeText(timeValue) {
  if (timeValue === "morning") return "早上 9 點到中午 12 點";
  if (timeValue === "afternoon") return "下午 1 點到下午 4 點";
  return timeValue || "";
}


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

  
  if (!user) {
    // token 無效/過期/沒登入
    localStorage.removeItem("token");
    window.location.href = "/";
    return;
  }

  // 2) 抓 booking
  const bookingData = await fetchBooking(token);
  renderBooking(bookingData);

  // 3) 綁定刪除按鈕（如果有 booking 才會顯示）
  const deleteBtn = document.getElementById("deleteBookingBtn");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", async () => {
      const ok = await deleteBooking(token);
      if (ok) {
        location.reload(); // 規格要求：刪除成功後 refresh page
      }
    });
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

async function fetchBooking(token) {
  try {
    const res = await fetch("/api/booking", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!res.ok) {
      // 403 也會進來（未登入）
      return null;
    }

    const data = await res.json();
    // Swagger：{ data: null } 代表沒有資料
    return data ? data.data : null;
  } catch (err) {
    console.error("fetchBooking error:", err);
    return null;
  }
}

function renderBooking(bookingData) {
  const statusEl = document.getElementById("bookingStatus");
  const infoEl = document.getElementById("bookingInfo");
  const checkoutBar = document.getElementById("checkoutBar");
  const totalPriceEl = document.getElementById("totalPrice");
  const dividerEl = document.querySelector(".divider"); // ✅ 直接抓 hr

  if (!bookingData) {
    // ✅ 空狀態：隱藏多餘區塊 + 套用空狀態樣式
    document.body.classList.add("empty-state");

    if (statusEl) statusEl.textContent = "目前沒有待預定的行程";
    if (infoEl) infoEl.style.display = "none";
    if (checkoutBar) checkoutBar.style.display = "none";
    if (dividerEl) dividerEl.style.display = "none";
    return;
  }

  // 有 booking

  // ✅ 有 booking：恢復顯示 + 移除空狀態樣式
  document.body.classList.remove("empty-state");

  if (statusEl) statusEl.textContent = "";
  if (infoEl) infoEl.style.display = "flex";
  if (checkoutBar) checkoutBar.style.display = "flex";
  if (dividerEl) dividerEl.style.display = "block";

  // attraction
  const name = bookingData.attraction?.name ?? "";
  const address = bookingData.attraction?.address ?? "";
  const image = bookingData.attraction?.image ?? "";

  const imgEl = document.getElementById("attrImage");
  if (imgEl) imgEl.src = image;

  setText("attrName", name);
  setText("attrAddress", address);

  // date/time/price
  setText("bookDate", bookingData.date ?? "");
  setText("bookTime", formatTimeText(bookingData.time));
  setText("bookPrice", `新台幣${bookingData.price ?? ""}元`);

  // total price
  if (totalPriceEl) totalPriceEl.textContent = String(bookingData.price ?? 0);
}


function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

async function deleteBooking(token) {
  try {
    const res = await fetch("/api/booking", {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    const data = await res.json().catch(() => null);

    if (res.ok && data && data.ok === true) {
      return true;
    }

    // 如果後端回 error + message
    if (data && data.message) alert(data.message);
    return false;
  } catch (err) {
    console.error("deleteBooking error:", err);
    return false;
  }
}