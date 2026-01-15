console.log("auth.js loaded");

function getNavLoginElement() {
    return document.getElementById("navLogin");
}


async function handleSignup() {
    // 1. 抓取 HTML 輸入框的值 (請確保你的 HTML id 正確)
    const name = document.querySelector("#signupName").value;
    const email = document.querySelector("#signupEmail").value;
    const password = document.querySelector("#signupPassword").value;
    const messageDiv = document.querySelector("#signupMessage"); // 顯示結果的文字區域

    // 2. 使用 fetch 發送資料
    try {
        const response = await fetch("/api/user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                "name": name,
                "email": email,
                "password": password
            })
        });

        const result = await response.json();

        // 3. 處理後端回傳結果
        if (response.ok) {
            messageDiv.innerText = "註冊成功，請登入";
            messageDiv.style.color = "green";
            
        } else {
            // 如果後端傳回 400 (Email重複)，會顯示 detail 裡的訊息
            //messageDiv.innerText = result.detail || "註冊失敗";
            //messageDiv.style.color = "red";

            let msg = "註冊失敗";

            // FastAPI 驗證錯誤（422） → detail 是陣列
            if (Array.isArray(result.detail) && result.detail.length > 0) {
                msg = result.detail[0].msg || msg;
            } else if (typeof result.detail === "string") {
                // 你自己在後端丟的 HTTPException(detail="xxx")
                msg = result.detail;
            }

            messageDiv.innerText = msg;
            messageDiv.style.color = "red";
        }
    } catch (error) {
        console.error("註冊發生錯誤:", error);
    }
}


async function handleLogin() {
    const email = document.querySelector("#loginEmail").value;
    const password = document.querySelector("#loginPassword").value;
    const messageDiv = document.querySelector("#loginMessage");

    try {
        const response = await fetch("/api/user/auth", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                "email": email,
                "password": password
            })
        });

        const result = await response.json();

        if (response.ok && result.token) {
            // --- 儲存 Token ---
            localStorage.setItem("token", result.token);
            
            // 修改 UI 文字
            document.querySelector("#navLogin").innerText = "登出系統";
            
            // 關閉彈窗 (假設你的關閉函式叫 closeAuthModal)
            closeAuthModal(); 
            
            // 4-2 規格建議可以重新整理頁面來確保狀態更新
            location.reload(); 
        } else {
            // 登入失敗顯示訊息
            messageDiv.innerText = result.message || "電子郵件或密碼輸入錯誤";
            messageDiv.style.color = "red";
        }
    } catch (error) {
        console.error("登入發生錯誤:", error);
    }
}

// modal開啟/關閉功能
const modal = document.getElementById("authModal");
const loginSection = document.getElementById("loginSection");
const signupSection = document.getElementById("signupSection");
const loginMessage = document.getElementById("loginMessage");
const signupMessage = document.getElementById("signupMessage");

function openAuthModal() {
    modal.classList.remove("hidden");

    // 預設顯示登入表單
    switchToLogin();

    // 清空訊息
    loginMessage.innerText = "";
    signupMessage.innerText = "";
}

function closeAuthModal() {
    modal.classList.add("hidden");
}


// 登入/註冊切換
function switchToSignup() {
    loginSection.classList.add("hidden");
    signupSection.classList.remove("hidden");

    loginMessage.innerText = "";
    signupMessage.innerText = "";
}

function switchToLogin() {
    signupSection.classList.add("hidden");
    loginSection.classList.remove("hidden");

    loginMessage.innerText = "";
    signupMessage.innerText = "";
}

// 點擊nav開啟modal
document.getElementById("navLogin").addEventListener("click", () => {
    openAuthModal();
});

//登出功能
function handleLogout() {
    // 清除 LocalStorage 中的 Token
    localStorage.removeItem("token");

    // 重整頁面
    location.reload();
}


// 未登入狀態 >> 顯示 登入/註冊
function setNavToLoginMode() {
    const navLogin = getNavLoginElement();

    if (!navLogin) return;  // 防呆+通用化設計

    navLogin.textContent = "登入/註冊";

    //點擊時打開彈窗
    navLogin.onclick = () => {
        openAuthModal();
    };
    
}

// 已登入狀態 >> 顯示 登出系統
function setNavToLogoutMode() {
    const navLogin = getNavLoginElement();
    
    if(!navLogin) return;

    navLogin.textContent = "登出系統"

    //點擊時登出
    navLogin.onclick = () => {
        handleLogout();
    };
}


async function initAuth() {
    const navLogin = getNavLoginElement();
    if (!navLogin) return;

    const token = localStorage.getItem("token");

    // 如果沒 token 顯示登入/註冊
    if(!token) {
        setNavToLoginMode();
        return;
    }

    try{
        // 如果有 token 帶去後端
        const response = await fetch("/api/user/auth", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const result = await response.json();

        // 回傳為null 視為未登入
        if (!result.data) {
            localStorage.removeItem("token");
            setNavToLoginMode();
        } else {
            // 有拿到 user 資料 視為已登入
            setNavToLogoutMode();
        }

    } catch (error) {
        console.error("檢查登入狀態發生錯誤", error);
        // 出錯時 當成未登入
        localStorage.removeItem("token");
        setNavToLoginMode();
    }
}

initAuth();


document.getElementById("navBooking")?.addEventListener("click", () => {
  const token = localStorage.getItem("token");
  if (!token) {
    openAuthModal();
    return;
  }
  window.location.href = "/booking";
});