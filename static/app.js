const authSection = document.getElementById("auth-section");
const tabLogin = document.getElementById("tab-login");
const tabSignup = document.getElementById("tab-signup");
const emailInput = document.getElementById("email-input");
const passwordInput = document.getElementById("password-input");
const authBtn = document.getElementById("auth-btn");
const authError = document.getElementById("auth-error");
const authNote = document.getElementById("auth-note");
const logoutBtn = document.getElementById("logout-btn");

const reasonSection = document.getElementById("reason-section");
const reasonInput = document.getElementById("reason-input");
const reasonBtn = document.getElementById("reason-btn");

const cardsSection = document.getElementById("cards-section");
const drawBtn = document.getElementById("draw-btn");
const cardSlots = document.querySelectorAll(".card");

const overviewSection = document.getElementById("overview-section");
const overviewBtn = document.getElementById("overview-btn");
const overviewText = document.getElementById("overview-text");

const statusEl = document.getElementById("status");

let token = sessionStorage.getItem("tarot_token");
let uuid = sessionStorage.getItem("tarot_uuid");
let drawCount = 0;
let mode = "login";

function setStatus(msg) {
  statusEl.textContent = msg;
}

function authHeaders() {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function showApp() {
  authSection.classList.add("hidden");
  reasonSection.classList.remove("hidden");
  logoutBtn.classList.remove("hidden");
}

function resetReadingUI() {
  reasonSection.classList.add("hidden");
  cardsSection.classList.add("hidden");
  overviewSection.classList.add("hidden");
  drawBtn.classList.remove("hidden");
  reasonInput.value = "";
  reasonBtn.disabled = false;
  drawBtn.disabled = false;
  overviewBtn.disabled = false;
  overviewText.textContent = "";
  drawCount = 0;
  cardSlots.forEach((slot) => {
    slot.classList.remove("revealed");
    slot.querySelector(".card-front").innerHTML = "";
    slot.querySelector(".card-name").textContent = "";
  });
}

function showAuth() {
  resetReadingUI();
  authSection.classList.remove("hidden");
  logoutBtn.classList.add("hidden");
  setStatus("");
}

function handleAuthFailure() {
  sessionStorage.removeItem("tarot_token");
  sessionStorage.removeItem("tarot_uuid");
  token = null;
  uuid = null;
  showAuth();
  authError.textContent = "Your session expired. Please sign in again.";
}

if (token) showApp();

tabLogin.addEventListener("click", () => {
  mode = "login";
  tabLogin.classList.add("active");
  tabSignup.classList.remove("active");
  authBtn.textContent = "Sign In";
  passwordInput.setAttribute("autocomplete", "current-password");
  authNote.classList.add("hidden");
  authError.textContent = "";
});

tabSignup.addEventListener("click", () => {
  mode = "signup";
  tabSignup.classList.add("active");
  tabLogin.classList.remove("active");
  authBtn.textContent = "Sign Up";
  passwordInput.setAttribute("autocomplete", "new-password");
  authNote.classList.remove("hidden");
  authError.textContent = "";
});

authBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();
  const password = passwordInput.value;
  if (!email || !password) {
    authError.textContent = "Email and password required.";
    return;
  }
  authBtn.disabled = true;
  authError.textContent = "";
  try {
    const res = await fetch(`/${mode}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || "Authentication failed");
    }
    if (!data.idToken) {
      throw new Error("No token returned by the server.");
    }
    token = data.idToken;
    sessionStorage.setItem("tarot_token", token);
    passwordInput.value = "";
    showApp();
  } catch (err) {
    authError.textContent = err.message;
  } finally {
    authBtn.disabled = false;
  }
});

logoutBtn.addEventListener("click", () => {
  sessionStorage.removeItem("tarot_token");
  sessionStorage.removeItem("tarot_uuid");
  token = null;
  uuid = null;
  showAuth();
});

async function ensureUuid() {
  if (uuid) return uuid;
  const res = await fetch("/get_id");
  const data = await res.json();
  uuid = typeof data === "string" ? data : String(data);
  sessionStorage.setItem("tarot_uuid", uuid);
  return uuid;
}

reasonBtn.addEventListener("click", async () => {
  const reason = reasonInput.value.trim();
  if (!reason) {
    setStatus("The stars need a reason to speak...");
    return;
  }
  reasonBtn.disabled = true;
  setStatus("Consulting the cosmos...");
  try {
    await ensureUuid();
    const res = await fetch("/reason", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ uuid, reason }),
    });
    if (res.status === 401) return handleAuthFailure();
    if (!res.ok) throw new Error("Reason rejected");
    reasonSection.classList.add("hidden");
    cardsSection.classList.remove("hidden");
    setStatus("Draw your first card.");
  } catch (err) {
    setStatus("The stars are silent... try again.");
    reasonBtn.disabled = false;
  }
});

drawBtn.addEventListener("click", async () => {
  if (drawCount >= 3) return;
  drawBtn.disabled = true;
  setStatus("Drawing from the deck...");
  try {
    const res = await fetch(`/get_card?uuid=${encodeURIComponent(uuid)}`, {
      headers: authHeaders(),
    });
    if (res.status === 401) return handleAuthFailure();
    const data = await res.json();
    const cards = data["Heres your card"];
    if (!Array.isArray(cards)) throw new Error("Unexpected response");
    const newest = cards[cards.length - 1];
    const slot = cardSlots[drawCount];
    const slug = newest.toLowerCase().replace(/ /g, "_");
    const front = slot.querySelector(".card-front");
    front.innerHTML = `<img src="/static/cards/${slug}.jpg" alt="${newest}">`;
    slot.querySelector(".card-name").textContent = newest;
    slot.classList.add("revealed");
    drawCount = cards.length;

    if (drawCount >= 3) {
      drawBtn.classList.add("hidden");
      overviewSection.classList.remove("hidden");
      setStatus("Your three cards have been drawn.");
    } else {
      drawBtn.disabled = false;
      setStatus(`Card ${drawCount} drawn. Draw ${3 - drawCount} more.`);
    }
  } catch (err) {
    setStatus("The deck resists... try again.");
    drawBtn.disabled = false;
  }
});

overviewBtn.addEventListener("click", async () => {
  overviewBtn.disabled = true;
  setStatus("Caine is interpreting the cards...");
  try {
    const res = await fetch(`/overview?uuid=${encodeURIComponent(uuid)}`, {
      headers: authHeaders(),
    });
    if (res.status === 401) return handleAuthFailure();
    const data = await res.json();
    const message = typeof data === "string" ? data : data.message;
    overviewText.textContent = message;
    setStatus("");
  } catch (err) {
    setStatus("Caine has fallen silent... try again.");
    overviewBtn.disabled = false;
  }
});
