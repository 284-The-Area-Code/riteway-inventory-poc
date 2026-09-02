const API_URL = "/api/replenishment";

const messageEl = document.getElementById("status-message");
const tableBody = document.getElementById("replenishment-body");
const explanationEl = document.getElementById("explanation");
const explanationBody = document.getElementById("explanation-body");

let records = [];
let activeFilter = "ALL";
let selectedSku = null;

function showMessage(text) {
  messageEl.hidden = !text;
  messageEl.textContent = text || "";
}

function formatNumber(value) {
  if (value === null || value === undefined) {
    return "Not available";
  }
  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }
  return number.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function formatStatus(status) {
  if (status === null || status === undefined || status === "") {
    return "Not available";
  }
  return status;
}

function formatWarning(warning) {
  if (warning === null || warning === undefined || warning === "") {
    return "";
  }
  return warning;
}

function countByStatus(items) {
  const counts = { STOCKOUT: 0, REORDER: 0, OK: 0 };
  for (const item of items) {
    if (counts[item.status] !== undefined) {
      counts[item.status] += 1;
    }
  }
  return counts;
}

function visibleRecords() {
  if (activeFilter === "ALL") {
    return records;
  }
  return records.filter(function (item) {
    return item.status === activeFilter;
  });
}

function renderSummary() {
  const counts = countByStatus(records);
  document.getElementById("count-stockout").textContent = counts.STOCKOUT;
  document.getElementById("count-reorder").textContent = counts.REORDER;
  document.getElementById("count-ok").textContent = counts.OK;
}

function renderTable() {
  const rows = visibleRecords();
  tableBody.replaceChildren();

  for (const item of rows) {
    const tr = document.createElement("tr");
    if (item.sku === selectedSku) {
      tr.classList.add("is-selected");
    }

    tr.innerHTML =
      "<td>" + item.sku + "</td>" +
      "<td>" + item.product_name + "</td>" +
      "<td>" + formatNumber(item.average_daily_demand) + "</td>" +
      "<td>" + formatNumber(item.lead_time_days) + "</td>" +
      "<td>" + formatNumber(item.on_hand) + "</td>" +
      "<td>" + formatNumber(item.safety_stock) + "</td>" +
      "<td>" + formatNumber(item.reorder_point) + "</td>" +
      "<td>" + statusCell(item) + "</td>" +
      "<td class=\"data-warning-cell\">" +
        escapeText(formatWarning(item.data_warning)) +
      "</td>";

    tr.addEventListener("click", function () {
      selectedSku = item.sku;
      renderTable();
      renderExplanation(item);
    });

    tableBody.appendChild(tr);
  }
}

function statusCell(item) {
  if (item.status === null || item.status === undefined || item.status === "") {
    return escapeText(formatStatus(item.status));
  }
  return (
    "<span class=\"badge badge-" + item.status + "\">" +
      escapeText(item.status) +
    "</span>"
  );
}

function escapeText(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function statusReason(item) {
  if (item.data_warning) {
    return "Insufficient sales history; a replenishment decision is not calculated.";
  }
  if (item.status === "STOCKOUT") {
    return "On hand is 0.";
  }
  if (item.status === "REORDER") {
    return "On hand is at or below the reorder point.";
  }
  if (item.status === "OK") {
    return "On hand is above the reorder point.";
  }
  return "";
}

function hideExplanation() {
  explanationEl.hidden = true;
}

function observedSalesDisplay(value) {
  if (value === null || value === undefined) {
    return "Not available";
  }
  return formatNumber(value) + "/day";
}

function renderExplanation(item) {
  explanationEl.hidden = false;
  const warningHtml = item.data_warning
    ? "<p class=\"data-warning\"><strong>Data warning:</strong> " +
      escapeText(item.data_warning) +
      "</p>"
    : "";
  explanationBody.innerHTML =
    "<p><strong>Product: " + escapeText(item.product_name) +
      " · SKU: " + escapeText(item.sku) + "</strong></p>" +
    warningHtml +
    "<p>" + escapeText(statusReason(item)) + "</p>" +
    "<dl>" +
      "<dt>Average observed sales</dt><dd>" +
        escapeText(observedSalesDisplay(item.average_daily_demand)) + "</dd>" +
      "<dt>Supplier lead time</dt><dd>" +
        escapeText(formatNumber(item.lead_time_days)) + " days</dd>" +
      "<dt>Lead-time demand</dt><dd>" +
        escapeText(formatNumber(item.lead_time_demand)) + "</dd>" +
      "<dt>Safety stock</dt><dd>" +
        escapeText(formatNumber(item.safety_stock)) + "</dd>" +
      "<dt>Reorder point</dt><dd>" +
        escapeText(formatNumber(item.reorder_point)) + "</dd>" +
      "<dt>On hand</dt><dd>" +
        escapeText(formatNumber(item.on_hand)) + "</dd>" +
    "</dl>" +
    "<p><strong>Decision: " + escapeText(formatStatus(item.status)) +
      "</strong></p>";

  explanationEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function setFilter(status) {
  activeFilter = status;
  document.querySelectorAll(".filters button").forEach(function (button) {
    button.classList.toggle("is-active", button.dataset.filter === status);
  });
  renderTable();

  const stillVisible = visibleRecords().some(function (item) {
    return item.sku === selectedSku;
  });
  if (!stillVisible) {
    hideExplanation();
  }
}

async function loadReplenishment() {
  showMessage("Loading replenishment data…");
  try {
    const response = await fetch(API_URL);
    if (!response.ok) {
      throw new Error("Request failed");
    }
    records = await response.json();
    showMessage("");
    renderSummary();
    renderTable();
  } catch (error) {
    records = [];
    showMessage("Unable to load replenishment data.");
    renderSummary();
    renderTable();
  }
}

document.querySelectorAll(".filters button").forEach(function (button) {
  button.addEventListener("click", function () {
    setFilter(button.dataset.filter);
  });
});

loadReplenishment();
