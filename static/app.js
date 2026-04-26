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

let uuid = sessionStorage.getItem("tarot_uuid");
let drawCount = 0;

function setStatus(msg) {
  statusEl.textContent = msg;
}

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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uuid, reason }),
    });
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
    const res = await fetch(`/get_card?uuid=${encodeURIComponent(uuid)}`);
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
    const res = await fetch(`/overview?uuid=${encodeURIComponent(uuid)}`);
    const data = await res.json();
    const message = typeof data === "string" ? data : data.message;
    overviewText.textContent = message;
    setStatus("");
  } catch (err) {
    setStatus("Caine has fallen silent... try again.");
    overviewBtn.disabled = false;
  }
});
