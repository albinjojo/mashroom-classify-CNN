/* Live Pi dashboard: reads the camera frame and model prediction from Flask. */
const $ = (id) => document.getElementById(id);
const video = $("videoFeed");
const placeholder = $("cameraPlaceholder");
const indicator = $("liveIndicator");
const scanOverlay = $("scanOverlay");
const detectCount = $("detectCount");
const badgeCount = $("badgeCount");
const btnStart = $("btnStart");
const btnStop = $("btnStop");
const resultSec = $("resultSection");
const galleryGrid = $("galleryGrid");
const galleryBadge = $("galleryBadge");
const btnExport = $("btnExportPDF");
const headerBadge = document.querySelector(".header-badge");

const streamImage = document.createElement("img");
streamImage.id = "piFrame";
streamImage.className = "video-feed hidden";
streamImage.alt = "Live Raspberry Pi camera feed";
video.replaceWith(streamImage);

const stats = {
  grown: $("statFullyGrown"), medium: $("statMedium"), bud: $("statBud"), bad: $("statBad"),
};
const rings = { grown: $("ringGrown"), medium: $("ringMedium"), bud: $("ringBud"), bad: $("ringBad") };
const values = { grown: 0, medium: 0, bud: 0, bad: 0 };
let connected = false;
let previousLabel = "";
let polling = null;
let lastBadFrame = "";

function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }
function normalise(label) { return String(label || "").toLowerCase(); }
function updateBadge(isLive) {
  headerBadge.innerHTML = `<span class="badge-dot"></span>${isLive ? "Pi Camera Live" : "Waiting for Pi Camera"}`;
}
function updateRing(key) {
  const max = Math.max(values.grown, values.medium, values.bud, values.bad, 1);
  rings[key].style.strokeDashoffset = 264 * (1 - values[key] / max);
}
function recordLabel(label) {
  const lower = normalise(label);
  let key = null;
  if (lower.includes("bad")) key = "bad";
  else if (lower.includes("bud")) key = "bud";
  else if (lower.includes("medium")) key = "medium";
  else if (lower.includes("good") || lower.includes("mature")) key = "grown";
  if (!key || label === previousLabel) return;
  values[key] += 1;
  stats[key].textContent = values[key];
  updateRing(key);
  if (key === "bad") addBadEvent(label);
}
function addBadEvent(label) {
  const src = `/api/frame.jpg?t=${Date.now()}`;
  lastBadFrame = src;
  const item = document.createElement("button");
  item.type = "button";
  item.className = "gallery-card fade-in-up";
  item.innerHTML = `<div class="gallery-card-img-wrap"><img src="${src}" alt="Detected bad mushroom"></div><div class="gallery-card-body"><div class="gallery-card-time">${new Date().toLocaleTimeString()}</div><div class="gallery-card-label">⚠ ${label}</div></div>`;
  item.addEventListener("click", () => window.open(lastBadFrame, "_blank"));
  galleryGrid.prepend(item);
  galleryBadge.textContent = `${values.bad} image${values.bad === 1 ? "" : "s"}`;
}
function startView() {
  connected = true;
  hide(placeholder); show(streamImage); show(indicator); show(scanOverlay); show(detectCount); show(resultSec); show(btnStop); hide(btnStart); show(btnExport);
  if (!polling) polling = setInterval(refresh, 350);
  refresh();
}
function stopView() {
  connected = false;
  if (polling) clearInterval(polling);
  polling = null;
  hide(streamImage); hide(indicator); hide(scanOverlay); hide(detectCount); show(placeholder); show(btnStart); hide(btnStop);
}
async function refresh() {
  try {
    const response = await fetch("/api/live", { cache: "no-store" });
    if (!response.ok) throw new Error("Dashboard API unavailable");
    const data = await response.json();
    updateBadge(Boolean(data.has_frame));
    if (!data.has_frame || !connected) return;
    streamImage.src = `/api/frame.jpg?t=${Date.now()}`;
    const label = data.label || "Waiting for detection";
    indicator.querySelector(".live-label").textContent = `${label} · ${Number(data.confidence || 0).toFixed(1)}%`;
    recordLabel(label);
    previousLabel = label;
    badgeCount.textContent = values.bad;
  } catch (error) {
    updateBadge(false);
    indicator.querySelector(".live-label").textContent = "Dashboard disconnected";
  }
}
function exportPDF() { window.print(); }
window.exportPDF = exportPDF;
btnStart.addEventListener("click", startView);
btnStop.addEventListener("click", stopView);
updateBadge(false);
