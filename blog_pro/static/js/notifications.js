let lastNotifId = 0;

const iconMap = new Map([
    ["comment", "💬"],
    ["newpost", "📝"],
    ["system", "⚙️"],
    ["error", "❌"],
    ["like", "♥"]

]);

function timeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000) - 7200;
    const intervals = [
        { label: 'year', secs: 31536000 },
        { label: 'month', secs: 2592000 },
        { label: 'day', secs: 86400 },
        { label: 'hour', secs: 3600 },
        { label: 'minute', secs: 60 },
    ];
    for (const i of intervals) {
        const count = Math.floor(seconds / i.secs);
        if (count >= 1) return `${count} ${i.label}${count > 1 ? 's' : ''} ago`;
    }
    return "Just now";
}
// تحميل أولي
window.addEventListener("DOMContentLoaded", () => {
    fetch("/get_latest_notification_id")
        .then(res => res.json())
        .then(data => {
            lastNotifId = data.last_id || 0;
            loadOldNotifications();
        });

    document.getElementById("notif-btn").addEventListener("click", toggleNotifList);
    document.getElementById("clear-notifs").addEventListener("click", clearNotifications);
});

// 🔹 تحميل الإشعارات القديمة
function loadOldNotifications() {
    fetch("/all_notifications")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("notif-items");
            const noNotif = document.getElementById("no-notifs");
            container.innerHTML = "";

            if (data.length === 0) {
                noNotif.style.display = "block";
            } else {
                noNotif.style.display = "none";
                data.forEach(n => {
                    let icon = iconMap.get(n.type) || "🔔";
                    container.insertAdjacentHTML("beforeend", `
                        <div class="notif-item notif-${n.type}" onclick="openNotifLink('${n.link || '#'}')">
                            <div class="notif-left">${icon}</div>
                            <div class="notif-right">
                                <div class="notif-msg">${n.message}</div>
                                <div class="notif-time">${timeAgo(n.time)}</div>
                            </div>
                        </div>
                    `);
                });
            }
            updateNotifCount(data.length);
        });
}

// 🔹 التحقق من إشعارات جديدة فقط
function checkNotifications() {
    fetch(`/get_notifications?since=${lastNotifId}`)
        .then(res => res.json())
        .then(data => {
            if (data.new_notifications?.length > 0) {
                data.new_notifications.forEach(n => {
                    showLiveNotification(n);
                    if (n.id > lastNotifId) lastNotifId = n.id;
                });
                loadOldNotifications(); // تحديث القائمة
            }
        })
        .catch(err => console.error("Error checking notifications:", err));
}

function showLiveNotification(notif) {
    const container = document.getElementById("live-notif-container");
    const div = document.createElement("div");
    div.className = `notif-toast notif-${notif.type}`;
    div.innerHTML = `
        <div class="notif-icon">🔔</div>
        <div class="notif-content">
            <div class="notif-title">${notif.type.toUpperCase()}</div>
            <div class="notif-message">${notif.message}</div>
            <div class="notif-time">${timeAgo(notif.time)}</div>
        </div>
    `;
    container.appendChild(div);

    // حركة ظهور + اختفاء
    setTimeout(() => {
        div.classList.add("fade-out");
        setTimeout(() => div.remove(), 600);
    }, 5000);
}

// فتح الرابط عند الضغط على الإشعار
function openNotifLink(link) {
    if (link && link !== "#") window.location.href = link;
}

function toggleNotifList() {
    const list = document.getElementById("notif-list");
    list.classList.toggle("hidden");
    if (!list.classList.contains("hidden")) {
        list.classList.add("slide-in");
        setTimeout(() => list.classList.remove("slide-in"), 300);
    }
}

function clearNotifications() {
    fetch("/clear_notifications", { method: "POST" })
        .then(() => {
            document.getElementById("notif-items").innerHTML = "";
            document.getElementById("no-notifs").style.display = "block";
            updateNotifCount(0);
        });
}

function updateNotifCount(count) {
    const counter = document.getElementById("notif-count");
    counter.innerText = count;
    counter.style.display = count > 0 ? "flex" : "none";
}

// setInterval(checkNotifications, 10000);