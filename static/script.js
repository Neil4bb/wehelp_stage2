let nextPage = 0;

// 防止重複載入的開關 (Loading Lock)。
// 當 API 正在抓資料時，把它設為 true，避免使用者滑太快導致重複發出請求
let isLoading = false; 

let currentKeyword = "";
let currentCategory = ""; 
let attractionContainer;
let searchInput;
let searchBtn;

document.addEventListener("DOMContentLoaded",() =>{
    attractionContainer = document.getElementById("attraction-container");
    searchInput = document.getElementById("search-input");
    searchBtn = document.getElementById("search-button");


    searchBtn.addEventListener("click", performSearch);

    searchInput.addEventListener("keydown",(event) => {
        //檢查按下的按鍵是否為Enter
        if (event.key === "Enter") {
            performSearch();
        }
    });

    
    fetchMRTs();
    fetchAttractions(0);
    setupObserver();
    fetchCategories();
});

async function fetchMRTs() {
    try {
        const response = await fetch("/api/mrts");
        const data = await response.json();
        const mrts = data.data

        renderMRTs(mrts);
    } catch (error) {
        console.error("無法取得捷運站資料", error);
    }
}

function renderMRTs(mrts) {
    const mrtList = document.getElementById("mrt-list");
    
    mrts.forEach(name => {
        const li = document.createElement("li");
        li.textContent = name;
        li.className = "mrt-item";

        li.addEventListener("click", () => {
            searchInput.value = name;

            performSearch();
        });

        mrtList.appendChild(li);
    });

}

async function fetchAttractions(page = 0) {
    
    //如果正在載入中，或沒有下一頁，就直接結束不執行
    if (isLoading || page === null) return;

    //  【上鎖】開始抓取資料，將開關設為 true
    isLoading = true;
    
    
    try {
        //  使用encodeURIComponent 來確保url完整傳到後端
        const url = `/api/attractions?page=${page}&keyword=${encodeURIComponent(currentKeyword)}&category=${encodeURIComponent(currentCategory)}`;
        const response = await fetch(url);
        
        //const response = await fetch(`/api/attractions?page=${page}&keyword=${currentKeyword}`);
        const data = await response.json();
        
        const attractions = data.data;
        renderAttractions(attractions);

        nextPage = data.nextPage;

    } catch (error){
        console.error("景點資料抓取失敗", error);
    } finally {
        //  【解鎖】無論成功或失敗，把開關打開
        isLoading = false;
    }
}

function renderAttractions(list) {

    list.forEach(item =>{
        
        const card = document.createElement("div");
        card.className = "attraction-item";

        //建立骨架
        card.innerHTML = `
            <div class="attraction-image-box">
                <img class="attr-img" src="" alt="">
                <div class="attraction-name-tag"></div>
            </div>
            <div class="attraction-info">
                <span class= "mrt-text"></span>
                <span class= "cat-text"></span>
            </div>
        `;

        //填入資料
        card.querySelector(".attr-img").src = item.images[0];
        card.querySelector(".attraction-name-tag").textContent = item.name;
        card.querySelector(".mrt-text").textContent = item.mrt || "無捷運站";
        card.querySelector(".cat-text").textContent = item.category;

        attractionContainer.appendChild(card);
    });
}


function setupObserver() {
    // 設定觀察選項
    const options = {
        root: null, // 以視窗 (viewport) 為基準
        rootMargin: "0px",
        threshold: 0.5 // 當哨兵 (Sentinel) 出現 50% 時就觸發
    };

    // 建立觀察器
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            // 觸發條件：
            // 1. 哨兵出現在畫面上 (isIntersecting)
            // 2. 還有下一頁 (nextPage !== null)
            // 不需檢查 isLoading，因為 fetchAttractions 內部第一行已經有了
            if (entry.isIntersecting && nextPage !== null) {
                // 呼叫抓取函式，抓全域變數記錄的「下一頁」
                fetchAttractions(nextPage);
            }
        });
    }, options);

    // 開始觀察：抓取那個隱形 div
    const target = document.querySelector("#footer-sentinel");
    if (target) {
        observer.observe(target);
    }
}

const categoryBtn = document.querySelector("#category");
const categoryPanel = document.querySelector("#category-panel");

// 切換面板顯示/隱藏
categoryBtn.addEventListener("click", (event) => {
    
    // 阻止事件冒泡
    event.stopPropagation();

    const currentDisplay = window.getComputedStyle(categoryPanel).display;

    if (currentDisplay === "block") {
        categoryPanel.style.display = "none";
    } else {
        categoryPanel.style.display = "block";
    }
});

// 當點擊頁面其他地方時，自動關閉面板
document.addEventListener("click", (event) => {
    if (!categoryPanel.contains(event.target)){
        categoryPanel.style.display = "none";
    }
});

async function fetchCategories() {
    try {
        const response = await fetch("/api/categories");
        const data = await response.json();
        renderCategories(data.data); // 拿到資料後交給 Render 處理
    } catch (error) {
        console.error("分類抓取失敗:", error);
    }
}

function renderCategories(categories) {
    const listContainer = document.querySelector("#category-list");
    const categoryPanel = document.querySelector("#category-panel");
    const categoryBtn = document.querySelector("#category");
    

    categories.forEach(cat => {
        const div = document.createElement("div");
        div.textContent = cat;
        div.className = "category-item";
        
        div.addEventListener("click", () => {
            categoryBtn.textContent = cat;
            categoryPanel.style.display = "none";

            currentCategory = cat;
            currentKeyword = ""; // 清空關鍵字
            searchInput.value = ""; // 清空input
            nextPage = 0;
            
            attractionContainer.innerHTML = "";

            fetchAttractions(0);
        });

        listContainer.appendChild(div);
    });
}



// 統一的搜尋執行函式
function performSearch() {
    currentKeyword = searchInput.value;
    nextPage = 0;
    attractionContainer.innerHTML = "";
    fetchAttractions(0);
}


const leftBtn = document.querySelector(".left-arrow");
const rightBtn = document.querySelector(".right-arrow");
const wrapper = document.querySelector(".mrt-list-wrapper");

leftBtn.addEventListener("click", () => {
    wrapper.scrollBy({ left: -wrapper.offsetWidth*0.8, behavior: 'smooth'});
});

rightBtn.addEventListener("click", () => {
    wrapper.scrollBy({ left: wrapper.offsetWidth*0.8, behavior: 'smooth'});
});