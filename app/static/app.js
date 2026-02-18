const rawHistory = window.__IP_HISTORY__ || [];

const history = rawHistory
  .map((entry) => ({
    ip: entry.ip,
    timestamp: new Date(entry.timestamp),
  }))
  .filter((entry) => entry.ip && !Number.isNaN(entry.timestamp.valueOf()))
  .sort((a, b) => b.timestamp - a.timestamp);

const totalSamples = document.getElementById("total-samples");
const ipChanges = document.getElementById("ip-changes");
const changeFrequency = document.getElementById("change-frequency");
const changeWindow = document.getElementById("change-window");
const latestIp = document.getElementById("latest-ip");
const timelineBody = document.getElementById("timeline-body");

const changeCount = history.reduce((count, entry, index, list) => {
  if (index === list.length - 1) {
    return count;
  }
  return entry.ip !== list[index + 1].ip ? count + 1 : count;
}, 0);

if (totalSamples) {
  totalSamples.textContent = history.length.toString();
}

if (ipChanges) {
  ipChanges.textContent = changeCount.toString();
}

if (changeFrequency) {
  if (history.length < 2 || changeCount === 0) {
    changeFrequency.textContent = "-";
  } else {
    const newest = history[0].timestamp;
    const oldest = history[history.length - 1].timestamp;
    const windowMs = Math.max(newest - oldest, 1);
    const perDay = (changeCount / windowMs) * 86400000;
    changeFrequency.textContent = `${perDay.toFixed(2)} / day`;
  }
}

if (changeWindow) {
  if (history.length < 2 || changeCount === 0) {
    changeWindow.textContent = "-";
  } else {
    const newest = history[0].timestamp;
    const oldest = history[history.length - 1].timestamp;
    const windowMs = Math.max(newest - oldest, 1);
    if (windowMs < 86400000) {
      const windowHours = windowMs / 3600000;
      changeWindow.textContent = `${changeCount} changes in ${windowHours.toFixed(2)} hours`;
    } else {
      const windowDays = windowMs / 86400000;
      changeWindow.textContent = `${changeCount} changes in ${windowDays.toFixed(2)} days`;
    }
  }
}

if (latestIp) {
  latestIp.textContent = history.length ? history[0].ip : "-";
}

if (timelineBody) {
  timelineBody.innerHTML = "";
  if (!history.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 3;
    cell.className = "empty";
    cell.textContent = "No samples yet.";
    row.appendChild(cell);
    timelineBody.appendChild(row);
  } else {
    history.forEach((entry, index) => {
      const previous = history[index + 1];
      const changed = previous ? entry.ip !== previous.ip : false;

      const row = document.createElement("tr");
      const timeCell = document.createElement("td");
      const ipCell = document.createElement("td");
      const changeCell = document.createElement("td");

      timeCell.textContent = entry.timestamp.toLocaleString("de-DE", {
        dateStyle: "medium",
        timeStyle: "short",
      });
      ipCell.textContent = entry.ip;

      const chip = document.createElement("span");
      chip.className = `change-chip${changed ? " changed" : ""}`;
      chip.textContent = changed ? "Changed" : "Stable";
      changeCell.appendChild(chip);

      row.appendChild(timeCell);
      row.appendChild(ipCell);
      row.appendChild(changeCell);

      timelineBody.appendChild(row);
    });
  }
}
