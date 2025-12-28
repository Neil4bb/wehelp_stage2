// 取得域名到問號之前的所有內容
const path = window.location.pathname;
// .split() 以字串切開 轉為array .pop()取陣列最後一個元素
const attractionId = path.split("/").pop();

let currentImageIndex = 0; //當前顯示圖片索引
let attractionImages = []; //用於存放圖片網址 左右切換圖片使用

console.log(`當前景點 ID : ${attractionId}`);


async function fetchAttraction() {

        try {
            const response = await fetch(`/api/attraction/${attractionId}`);
            const data = await response.json();

            if(data.data) {
                renderAttraction(data.data);
            }

        } catch (error) {
            console.error("無法取得景點資料", error);
        }

}

function renderAttraction(item) {
    const name = document.querySelector("#attr-name");
    const catAndMrt = document.querySelector("#attr-cat-mrt");
    const description = document.querySelector("#attr-description");
    const address = document.querySelector("#attr-address");
    const transport = document.querySelector("#attr-transport");

    name.textContent = item.name;
    catAndMrt.textContent = `${item.category} at ${item.mrt}`;
    description.textContent = item.description;
    address.textContent = item.address;
    transport.textContent = item.transport;

    initSlideshow(item.images);
    
    /*
    const imageWrapper = document.querySelector(".image-wrapper");
    imageWrapper.innerHTML = "";
    
    //第一張圖試做
    const firstImg = document.createElement("img");
    firstImg.src = item.images[0];
    firstImg.alt = item.name;
    firstImg.style.width = "100%";
    imageWrapper.appendChild(firstImg);

    //圖片輪播器試作
    attractionImages = item.images;

    const indicatorsContainer = document.querySelector("#indicators-container");
    indicatorsContainer.innerHTML = "";

    for (let i=0; i<attractionImages.length; i++) {
        let newDiv = document.createElement("div");
        newDiv.classList.add("indicator-bar");

        //預設第一張圖的線段為active
        if (i === 0) {
            newDiv.classList.add("active");
        }

        indicatorsContainer.appendChild(newDiv);
    }
    */
}

function initSlideshow(images) {
    attractionImages = images;
    currentImageIndex = 0;  //重置索引

    const indicatorsContainer = document.querySelector(".indicators-container");
    indicatorsContainer.innerHTML = "";
    attractionImages.forEach((_, i) => {
       const bar = document.createElement("div");
       bar.classList.add("indicator-bar");
       if (i === 0) bar.classList.add("active");
       indicatorsContainer.appendChild(bar); 
    });

    //顯示第一張圖
    showImage(0);
}

function showImage(index) {

    const mainImg = document.querySelector("#main-image");
    mainImg.src = attractionImages[index];

    // 更新 bar 狀態
    const bars = document.querySelectorAll(".indicator-bar");
    bars.forEach((bar, i) => {
        if (i === index) {
            bar.classList.add("active");
        } else {
            bar.classList.remove("active");
        }
    });

    currentImageIndex = index;

}

function setupSlideShowListener() {
    const rightArrow = document.querySelector(".right-arrow");
    const leftArrow = document.querySelector(".left-arrow");

    rightArrow.addEventListener("click", () => {
        currentImageIndex++;
        if (currentImageIndex >= attractionImages.length) {
            currentImageIndex = 0; //超過張數 返回第一張
        }

        showImage(currentImageIndex);
    });

    leftArrow.addEventListener("click", () => {
        currentImageIndex--;
        if (currentImageIndex < 0) {
            currentImageIndex = attractionImages.length - 1;
        }

        showImage(currentImageIndex);
    });
    
}

function setupBookingPriceListener() {
    const timeRadios = document.querySelectorAll('input[name="time"]');
    const price = document.querySelector("#booking-price");

    timeRadios.forEach(radio => {
        // 瀏覽器在事件發生瞬間，會自動把產生的事件物件，丟進箭頭函式當作第一個參數
        radio.addEventListener("change", (event) => {
            if (event.target.value === "morning") {
                // event 為事件 event.target才會抓到HTML元素
                price.textContent = "2000";
            } else {
                price.textContent = "2500";
            }
        });

    });

}

document.addEventListener("DOMContentLoaded", () => {
    fetchAttraction();
    setupBookingPriceListener();
    setupSlideShowListener();
});
