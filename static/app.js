"use strict";

const $ = (id) => document.getElementById(id);
const state = { scenarios: [], current: 0, a: "Share", b: "Share" };
const display = (value) => value === "Don't Share" ? "Don’t Share" : value;
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));
const scenario = () => state.scenarios[state.current];
const selectedOutcome = () => scenario().outcomes.find((outcome) => outcome.aStrategy === state.a && outcome.bStrategy === state.b);
const decisionPair = (outcome) => `${display(outcome.aStrategy)} / ${display(outcome.bStrategy)}`;

function createControls() {
  const picker = $("scenario-picker");
  picker.replaceChildren();
  state.scenarios.forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "scenario-button";
    button.dataset.scenario = index;
    button.setAttribute("aria-pressed", "false");
    button.innerHTML = `<span class="scenario-number">${escapeHTML(item.number)}</span><span class="scenario-text"><strong>${escapeHTML(item.name)}</strong><small>${escapeHTML(item.tagline)}</small></span><span class="scenario-radio" aria-hidden="true"></span>`;
    picker.append(button);
  });
  const matrix = $("payoff-matrix");
  matrix.replaceChildren();
  ["Share", "Don't Share"].forEach((a, row) => {
    const label = document.createElement("div");
    label.className = "matrix-row-label";
    label.innerHTML = `<small>ORG A</small>${escapeHTML(display(a))}`;
    matrix.append(label);
    [0, 1].forEach((column) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "matrix-cell";
      button.dataset.outcome = row * 2 + column;
      matrix.append(button);
    });
  });
  renderComparison();
}

function renderMatrix() {
  const current = scenario();
  document.querySelectorAll(".matrix-cell").forEach((cell, index) => {
    const outcome = current.outcomes[index];
    const active = outcome.aStrategy === state.a && outcome.bStrategy === state.b;
    cell.classList.toggle("is-nash", outcome.isNash);
    cell.classList.toggle("is-best", outcome.isSocialBest);
    cell.setAttribute("aria-pressed", String(active));
    cell.setAttribute("aria-label", `A: ${display(outcome.aStrategy)}. B: ${display(outcome.bStrategy)}. A earns ${outcome.a}, B earns ${outcome.b}. Combined score ${outcome.total}.${outcome.isNash ? " Nash equilibrium." : " Not a Nash equilibrium."}${outcome.isSocialBest ? " Highest combined score." : ""}`);
    cell.innerHTML = `${active ? '<span class="selection-marker">Selected</span>' : ""}<span class="score-pair"><span class="pair-member pair-a"><small>A</small><strong>${outcome.a}</strong></span><span class="pair-divider" aria-hidden="true"></span><span class="pair-member pair-b"><small>B</small><strong>${outcome.b}</strong></span></span><span class="cell-badges">${outcome.isNash ? '<span class="badge badge-ne"><i class="badge-point"></i>Nash equilibrium</span>' : ""}${outcome.isSocialBest ? '<span class="badge badge-best">Highest combined</span>' : ""}</span>`;
  });
}

function renderDeviation(player, outcome) {
  const isA = player === "A";
  const currentScore = isA ? outcome.a : outcome.b;
  const change = isA ? outcome.switchA : outcome.switchB;
  const improves = change.gain > 0;
  const explanation = improves
    ? `Gains ${change.gain} point${change.gain === 1 ? "" : "s"} by switching alone.`
    : change.gain < 0
      ? `Loses ${Math.abs(change.gain)} point${change.gain === -1 ? "" : "s"} by switching; no reason to change.`
      : "Same score after switching; no improvement.";
  $(`deviation-${player.toLowerCase()}`).innerHTML = `<span class="org-avatar avatar-${player.toLowerCase()}">${player}</span><div class="deviation-content"><p>Switch to <b>${escapeHTML(display(change.strategy))}</b>, with ${isA ? "B" : "A"} fixed.</p><span class="${improves ? "" : "no-gain"}">${escapeHTML(explanation)}</span></div><span class="switch-score" aria-label="Current score ${currentScore}; score after switching ${change.score}">${currentScore}<span aria-hidden="true">→</span>${change.score}</span>`;
}

function renderDecisions() {
  const outcome = selectedOutcome();
  document.querySelectorAll("[data-player]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.choice === (button.dataset.player === "A" ? state.a : state.b)));
  });
  $("score-a").textContent = outcome.a;
  $("score-b").textContent = outcome.b;
  $("score-total").textContent = outcome.total;
  $("outcome-verdict").classList.toggle("stable", outcome.isNash);
  $("verdict-symbol").textContent = outcome.isNash ? "✓" : "!";
  $("verdict-title").textContent = outcome.isNash ? "This is a Nash equilibrium" : "This is not a Nash equilibrium";
  const improving = [outcome.switchA.gain > 0 && "A", outcome.switchB.gain > 0 && "B"].filter(Boolean);
  $("verdict-description").textContent = outcome.isNash
    ? "Neither organization can earn more by changing its decision alone."
    : `${improving.length === 2 ? "Both organizations can" : `Organization ${improving[0]} can`} earn more by switching alone. ${outcome.isSocialBest ? "The highest combined score is not necessarily stable." : "See the individual incentives below."}`;
  renderDeviation("A", outcome);
  renderDeviation("B", outcome);
}

function renderFindings() {
  const current = scenario();
  $("equilibrium-summary").innerHTML = current.outcomes.filter((outcome) => outcome.isNash).map((outcome) => `<div class="equilibrium-line">${escapeHTML(decisionPair(outcome))}<span class="equilibrium-scores">(${outcome.a}, ${outcome.b})</span></div>`).join("");
  const dominant = current.dominant.A;
  $("dominant-summary").textContent = dominant ? `${display(dominant)}, for both` : "No dominant strategy";
  $("dominant-explanation").textContent = dominant
    ? "This choice earns more, whatever the other organization chooses."
    : "The best choice depends on what the other organization does.";
  $("highest-total").textContent = current.highestTotal;
  const highest = current.outcomes.filter((outcome) => outcome.isSocialBest);
  $("highest-outcome").textContent = highest.map((outcome) => `${decisionPair(outcome)} gives ${outcome.a} + ${outcome.b}.`).join(" ");
  $("best-responses").innerHTML = ["A", "B"].map((player) => `<div><strong>Organization ${player}</strong>${current.bestResponses[player].map((response) => `<p>If ${player === "A" ? "B" : "A"} chooses ${escapeHTML(display(response.opponent))}:<br><b>${escapeHTML(response.choices.map(display).join(" or "))}</b></p>`).join("")}</div>`).join("");
}

function renderChart() {
  const current = scenario();
  const baseline = 166;
  const unit = 13;
  const labels = [["Both", "share"], ["Only A", "shares"], ["Only B", "shares"], ["Neither", "shares"]];
  const description = current.outcomes.map((outcome) => `${decisionPair(outcome)}: A ${outcome.a}, B ${outcome.b}`).join(". ");
  let content = `<svg viewBox="0 0 540 224" role="img" aria-labelledby="chart-title chart-desc"><title id="chart-title">${escapeHTML(current.name)} payoff comparison</title><desc id="chart-desc">${escapeHTML(description)}. Vertical scale is zero to ten utility points.</desc>`;
  [0, 2, 4, 6, 8, 10].forEach((tick) => {
    const y = baseline - tick * unit;
    content += `<line x1="35" x2="527" y1="${y}" y2="${y}" stroke="#e9edf4" stroke-width="1"/><text x="25" y="${y + 3}" text-anchor="end" font-family="Arial,sans-serif" font-size="9" fill="#94a0b3">${tick}</text>`;
  });
  current.outcomes.forEach((outcome, index) => {
    const center = 98 + index * 121;
    const active = outcome.aStrategy === state.a && outcome.bStrategy === state.b;
    if (active) content += `<rect x="${center - 47}" y="17" width="94" height="195" rx="7" fill="#edf2ff" fill-opacity=".8"/>`;
    [[outcome.a, center - 27, "#4269e0"], [outcome.b, center + 4, "#ce8b64"]].forEach(([score, x, color]) => {
      content += `<rect x="${x}" y="${baseline - score * unit}" width="23" height="${score * unit}" rx="3" fill="${color}"/><text x="${x + 11.5}" y="${baseline - score * unit - 7}" text-anchor="middle" font-family="Arial,sans-serif" font-weight="600" font-size="10" fill="${color}">${score}</text>`;
    });
    content += `<text x="${center}" y="188" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" fill="#63718a"><tspan x="${center}">${labels[index][0]}</tspan><tspan x="${center}" dy="13">${labels[index][1]}</tspan></text>`;
  });
  $("outcome-chart").innerHTML = content + "</svg>";
}

function renderComparison() {
  $("comparison-body").innerHTML = state.scenarios.map((item, index) => {
    const equilibria = item.outcomes.filter((outcome) => outcome.isNash);
    return `<tr data-comparison="${index}"><td><div class="scenario-table-name"><span>${escapeHTML(item.number)}</span><strong>${escapeHTML(item.name)}</strong></div></td><td>${escapeHTML(item.dominant.A ? display(item.dominant.A) : "None — depends on the other")}</td><td>${equilibria.map((outcome) => `<span class="table-equilibrium">${escapeHTML(decisionPair(outcome))} <span class="equilibrium-scores">(${outcome.a}, ${outcome.b})</span></span>`).join("")}</td><td><span class="table-total">${item.highestTotal}</span><span class="table-total-label">utility points</span></td></tr>`;
  }).join("");
}

function renderScenario() {
  const current = scenario();
  document.querySelectorAll("[data-scenario]").forEach((button) => button.setAttribute("aria-pressed", String(Number(button.dataset.scenario) === state.current)));
  document.querySelectorAll("[data-comparison]").forEach((row) => row.classList.toggle("active-row", Number(row.dataset.comparison) === state.current));
  $("scenario-change").textContent = current.change;
  $("scenario-title").textContent = current.headline;
  $("scenario-description").textContent = current.description;
  $("scenario-caption").textContent = current.caption;
  $("scenario-takeaway").textContent = current.takeaway;
  $("scenario-assumption").textContent = current.assumption;
  renderFindings();
  renderOutcome();
}

function renderOutcome() {
  renderMatrix();
  renderDecisions();
  renderChart();
  const outcome = selectedOutcome();
  $("live-announcement").textContent = `${scenario().name}. A chooses ${display(state.a)}, B chooses ${display(state.b)}. A earns ${outcome.a}, B earns ${outcome.b}; combined score ${outcome.total}. ${outcome.isNash ? "Nash equilibrium: neither can improve by switching alone." : "Not a Nash equilibrium: at least one can improve by switching alone."}`;
}

function chooseScenario(index) {
  state.current = index;
  state.a = "Share";
  state.b = "Share";
  renderScenario();
}

async function loadExperiment() {
  $("loading").hidden = false;
  $("load-error").hidden = true;
  $("dashboard").hidden = true;
  $("retry-button").disabled = true;
  $("connection-label").textContent = "Connecting to Python";
  $("connection-dot").style.background = "#9aa4b4";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch("/api/scenarios", { cache: "no-store", signal: controller.signal });
    if (!response.ok) throw new Error("Analysis unavailable");
    const payload = await response.json();
    if (!Array.isArray(payload.scenarios) || payload.scenarios.length !== 3 || payload.scenarios.some((item) => !Array.isArray(item.outcomes) || item.outcomes.length !== 4)) {
      throw new Error("Incomplete analysis");
    }
    state.scenarios = payload.scenarios;
    state.current = 0;
    state.a = "Share";
    state.b = "Share";
    createControls();
    renderScenario();
    $("dashboard").hidden = false;
    $("connection-label").textContent = "Calculated with Python";
    $("connection-dot").style.background = "#159b7d";
  } catch (_error) {
    $("load-error").hidden = false;
    $("connection-label").textContent = "Analysis unavailable";
    $("connection-dot").style.background = "#bb7d39";
  } finally {
    clearTimeout(timeout);
    $("loading").hidden = true;
    $("retry-button").disabled = false;
  }
}

$("scenario-picker").addEventListener("click", (event) => {
  const button = event.target.closest("[data-scenario]");
  if (button) chooseScenario(Number(button.dataset.scenario));
});
$("payoff-matrix").addEventListener("click", (event) => {
  const button = event.target.closest("[data-outcome]");
  if (!button) return;
  const outcome = scenario().outcomes[Number(button.dataset.outcome)];
  state.a = outcome.aStrategy;
  state.b = outcome.bStrategy;
  renderOutcome();
});
document.querySelectorAll("[data-player]").forEach((button) => button.addEventListener("click", () => {
  if (button.dataset.player === "A") state.a = button.dataset.choice;
  else state.b = button.dataset.choice;
  renderOutcome();
}));
$("reset-button").addEventListener("click", () => {
  chooseScenario(0);
  $("best-responses").closest("details").open = false;
});
$("retry-button").addEventListener("click", loadExperiment);
loadExperiment();
