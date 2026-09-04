import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a local Slack request review page")
    parser.add_argument("input", type=Path, help="Request review JSON")
    parser.add_argument("output", type=Path, help="Output HTML")
    return parser.parse_args()


def create_slack_url(workspace_url: str, channel_id: str, message_ts: str, thread_ts: str | None) -> str:
    path = f"{workspace_url.rstrip('/')}/archives/{channel_id}/p{message_ts.replace('.', '')}"
    if not thread_ts or thread_ts == message_ts:
        return path
    return f"{path}?{urlencode({'thread_ts': thread_ts, 'cid': channel_id})}"


def parse_review_data(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    channel = data["channel"]
    channel_id = channel["id"]
    workspace_url = channel["workspace_url"]
    requests = data["requests"]
    seen_ids: set[str] = set()

    for request in requests:
        request_id = request["id"]
        if request_id in seen_ids:
            raise ValueError(f"Duplicate request id: {request_id}")
        seen_ids.add(request_id)
        request["message_url"] = create_slack_url(
            workspace_url,
            channel_id,
            request["message_ts"],
            request.get("thread_ts"),
        )
        completion_ts = request.get("completion_message_ts")
        request["completion_url"] = (
            create_slack_url(
                workspace_url,
                channel_id,
                completion_ts,
                request.get("completion_thread_ts"),
            )
            if completion_ts
            else ""
        )
        request["requester"] = ", ".join(request.get("requesters", []))

    return data


def create_html(data: dict[str, Any]) -> str:
    title = data.get("title") or "Slack request review"
    channel = data["channel"]
    window = data["window"]
    requests = data["requests"]
    storage_source = f"{channel['id']}:{window['start']}:{window['end']}"
    storage_key = f"slack-request-review-{hashlib.sha256(storage_source.encode()).hexdigest()[:16]}"
    payload = json.dumps(requests, ensure_ascii=False).replace("</", "<\\/")
    metadata = json.dumps(
        {
            "title": title,
            "channelName": channel.get("name") or channel["id"],
            "start": window["start"],
            "end": window["end"],
            "timezone": window.get("timezone", ""),
            "storageKey": storage_key,
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")

    template = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root {
    color-scheme: light dark;
    --bg: #f6f5f2;
    --panel: #fff;
    --text: #1d1f24;
    --muted: #686b73;
    --border: #d9d7d0;
    --accent: #5b4bb7;
    --accent-soft: #eeeafd;
    --yes-bg: #e6f6ec;
    --yes-text: #176a3a;
    --no-bg: #f7e8e5;
    --no-text: #8c2f23;
    --shadow: 0 1px 3px rgb(23 22 18 / 8%);
}
@media (prefers-color-scheme: dark) {
    :root {
        --bg: #171718;
        --panel: #222224;
        --text: #f2f0eb;
        --muted: #aaa8a2;
        --border: #3b3a3d;
        --accent: #b6a7ff;
        --accent-soft: #332d52;
        --yes-bg: #163e29;
        --yes-text: #9ae1b4;
        --no-bg: #4a2622;
        --no-text: #f3aaa0;
        --shadow: 0 1px 3px rgb(0 0 0 / 30%);
    }
}
* { box-sizing: border-box; }
body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font: 14px/1.45 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
main { max-width: 1900px; margin: 0 auto; padding: 24px; }
h1 { margin: 0 0 4px; font-size: 25px; line-height: 1.2; }
p { margin: 0; }
.intro { color: var(--muted); margin-bottom: 18px; }
.toolbar {
    display: grid;
    grid-template-columns: minmax(260px, 2fr) repeat(5, minmax(145px, 1fr));
    gap: 10px;
    padding: 14px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: var(--shadow);
}
label { display: grid; gap: 5px; color: var(--muted); font-size: 12px; font-weight: 600; }
input, select, textarea, button { font: inherit; color: var(--text); }
input, select, textarea {
    width: 100%;
    border: 1px solid var(--border);
    border-radius: 7px;
    background: var(--panel);
    padding: 8px 10px;
}
input:focus, select:focus, textarea:focus, button:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
}
.actions, .bulk-actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin: 12px 0;
}
.bulk-actions {
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 9px;
    background: var(--panel);
}
.bulk-actions select { width: 190px; }
button, .button {
    border: 1px solid var(--border);
    border-radius: 7px;
    background: var(--panel);
    padding: 7px 10px;
    cursor: pointer;
    text-decoration: none;
}
button:hover, .button:hover { border-color: var(--accent); }
button:disabled { cursor: not-allowed; opacity: 0.5; }
.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
#summary { margin-left: auto; color: var(--muted); }
#save-status { min-height: 20px; color: var(--muted); }
.table-wrap {
    overflow: auto;
    max-height: calc(100vh - 295px);
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--panel);
    box-shadow: var(--shadow);
}
table { width: 100%; min-width: 1780px; border-collapse: separate; border-spacing: 0; }
th, td { border-bottom: 1px solid var(--border); padding: 10px; text-align: left; vertical-align: top; }
th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: var(--panel);
    color: var(--muted);
    font-size: 12px;
    white-space: nowrap;
}
th button {
    display: inline-flex;
    gap: 5px;
    border: 0;
    padding: 0;
    color: inherit;
    font-size: inherit;
    font-weight: 700;
    background: transparent;
}
tbody tr:hover { background: color-mix(in srgb, var(--accent-soft) 40%, transparent); }
tbody tr:last-child td { border-bottom: 0; }
a { color: var(--accent); }
.select-cell { width: 42px; text-align: center; }
.select-cell input { width: auto; }
.request-name { min-width: 190px; font-weight: 700; }
.description { min-width: 300px; max-width: 430px; }
.area { min-width: 145px; color: var(--muted); }
.requester { min-width: 165px; }
.related { min-width: 230px; }
.review { min-width: 170px; }
.notes { min-width: 280px; }
.notes textarea { min-height: 74px; resize: vertical; }
.badge {
    display: inline-flex;
    min-width: 42px;
    justify-content: center;
    border-radius: 999px;
    padding: 3px 8px;
    font-size: 12px;
    font-weight: 700;
}
.badge.yes { color: var(--yes-text); background: var(--yes-bg); }
.badge.no { color: var(--no-text); background: var(--no-bg); }
.new-request { color: var(--no-text); font-weight: 700; }
.link-list { display: grid; gap: 4px; }
.empty { padding: 40px; text-align: center; color: var(--muted); }
@media (max-width: 1200px) {
    main { padding: 14px; }
    .toolbar { grid-template-columns: 1fr 1fr; }
    .toolbar label:first-child { grid-column: 1 / -1; }
    #summary { width: 100%; margin-left: 0; }
    .table-wrap { max-height: calc(100vh - 420px); }
}
</style>
</head>
<body>
<main>
    <h1 id="page-title"></h1>
    <p id="intro" class="intro"></p>

    <section class="toolbar" aria-label="Table filters">
        <label>Search
            <input id="search" type="search" placeholder="Search requests, descriptions, people, or notes">
        </label>
        <label>Area
            <select id="area-filter"><option value="">All areas</option></select>
        </label>
        <label>Completion
            <select id="completed-filter">
                <option value="">All requests</option>
                <option value="yes">Completed</option>
                <option value="no">Open</option>
            </select>
        </label>
        <label>Feature request
            <select id="existing-filter">
                <option value="">All tracker states</option>
                <option value="yes">Already tracked</option>
                <option value="no">Needs a request</option>
            </select>
        </label>
        <label>Match confidence
            <select id="confidence-filter">
                <option value="">All confidence levels</option>
                <option value="high">High</option>
                <option value="moderate">Moderate</option>
                <option value="low">Low</option>
            </select>
        </label>
        <label>Review status
            <select id="review-filter">
                <option value="">All review states</option>
                <option value="unreviewed">Unreviewed</option>
                <option value="create">Create request</option>
                <option value="update">Update existing request</option>
                <option value="none">No action</option>
            </select>
        </label>
    </section>

    <div class="actions">
        <button id="reset-filters" type="button">Reset filters</button>
        <button id="copy-review" type="button" class="primary">Copy review summary</button>
        <button id="export-review" type="button">Export review</button>
        <label class="button" for="import-review">Import review</label>
        <input id="import-review" type="file" accept="application/json" hidden>
        <span id="summary"></span>
    </div>

    <div class="bulk-actions" aria-label="Bulk review actions">
        <strong id="selection-summary">0 selected</strong>
        <select id="bulk-review-status" aria-label="Bulk review status">
            <option value="">Choose review status</option>
            <option value="unreviewed">Unreviewed</option>
            <option value="create">Create request</option>
            <option value="update">Update existing request</option>
            <option value="none">No action</option>
        </select>
        <button id="apply-bulk-status" type="button" disabled>Apply to selected</button>
        <button id="clear-selection" type="button" disabled>Clear selection</button>
    </div>

    <p id="save-status" role="status" aria-live="polite">Export the review before moving to another browser or device.</p>

    <div class="table-wrap">
        <table>
            <thead><tr id="headers"></tr></thead>
            <tbody id="request-body"></tbody>
        </table>
        <div id="empty-state" class="empty" hidden>No requests match these filters.</div>
    </div>
</main>
<script>
const requestRows = __REQUEST_DATA__;
const metadata = __METADATA__;
const storageKey = metadata.storageKey;
const areaOrder = [...new Set(requestRows.map((request) => request.area))];
const reviewOptions = [
    ["unreviewed", "Unreviewed"],
    ["create", "Create request"],
    ["update", "Update existing request"],
    ["none", "No action"],
];
const columns = [
    ["name", "Request", "request-name"],
    ["description", "Description", "description"],
    ["area", "Area", "area"],
    ["requester", "Requester", "requester"],
    ["completed", "Completed", ""],
    ["existing", "In feature requests", ""],
    ["match_confidence", "Match confidence", ""],
    ["related_name", "Related feature request", "related"],
    ["reviewStatus", "Review status", "review"],
    ["notes", "Notes", "notes"],
];

let reviews = getStoredReviews();
let selectedRequestIds = new Set();
let sortKey = "area";
let sortDirection = "asc";

const elements = {
    area: document.querySelector("#area-filter"),
    completed: document.querySelector("#completed-filter"),
    existing: document.querySelector("#existing-filter"),
    confidence: document.querySelector("#confidence-filter"),
    review: document.querySelector("#review-filter"),
    search: document.querySelector("#search"),
    body: document.querySelector("#request-body"),
    headers: document.querySelector("#headers"),
    empty: document.querySelector("#empty-state"),
    summary: document.querySelector("#summary"),
    status: document.querySelector("#save-status"),
    selectionSummary: document.querySelector("#selection-summary"),
    bulkStatus: document.querySelector("#bulk-review-status"),
    applyBulkStatus: document.querySelector("#apply-bulk-status"),
    clearSelection: document.querySelector("#clear-selection"),
};

document.title = metadata.title;
document.querySelector("#page-title").textContent = metadata.title;
document.querySelector("#intro").textContent = `${requestRows.length} requests from ${metadata.channelName}, ${metadata.start} through ${metadata.end}${metadata.timezone ? ` (${metadata.timezone})` : ""}. Notes and review status save in this browser.`;

function getStoredReviews() {
    try {
        return JSON.parse(localStorage.getItem(storageKey) || "{}");
    } catch {
        return {};
    }
}

function getReview(request) {
    return reviews[request.id] || { reviewStatus: "unreviewed", notes: "", updatedAt: null };
}

function saveReviews(statusText) {
    localStorage.setItem(storageKey, JSON.stringify(reviews));
    elements.status.textContent = statusText;
    updateReviewSummary();
}

function saveReview(request, changes) {
    reviews[request.id] = { ...getReview(request), ...changes, updatedAt: new Date().toISOString() };
    saveReviews("Review saved locally.");
}

function createLink(label, href) {
    const link = document.createElement("a");
    link.textContent = label;
    link.href = href;
    link.target = "_blank";
    link.rel = "noreferrer";
    return link;
}

function createBadge(value) {
    const badge = document.createElement("span");
    badge.className = `badge ${value ? "yes" : "no"}`;
    badge.textContent = value ? "Yes" : "No";
    return badge;
}

function getSortableValue(request, key) {
    const review = getReview(request);
    if (key === "area") {
        return areaOrder.indexOf(request.area);
    }
    if (key === "reviewStatus" || key === "notes") {
        return review[key] || "";
    }
    return request[key];
}

function compareRequests(left, right) {
    const leftValue = getSortableValue(left, sortKey);
    const rightValue = getSortableValue(right, sortKey);
    const direction = sortDirection === "asc" ? 1 : -1;
    if (typeof leftValue === "boolean") {
        return (Number(leftValue) - Number(rightValue)) * direction;
    }
    if (typeof leftValue === "number") {
        const difference = (leftValue - rightValue) * direction;
        return difference || left.name.localeCompare(right.name);
    }
    return String(leftValue).localeCompare(String(rightValue), undefined, { sensitivity: "base" }) * direction;
}

function filterRequests() {
    const search = elements.search.value.trim().toLowerCase();
    return requestRows.filter((request) => {
        const review = getReview(request);
        const searchableText = [request.name, request.description, request.requester, request.related_name, request.area, review.notes].join(" ").toLowerCase();
        return (!search || searchableText.includes(search))
            && (!elements.area.value || request.area === elements.area.value)
            && (!elements.completed.value || request.completed === (elements.completed.value === "yes"))
            && (!elements.existing.value || request.existing === (elements.existing.value === "yes"))
            && (!elements.confidence.value || request.match_confidence === elements.confidence.value)
            && (!elements.review.value || review.reviewStatus === elements.review.value);
    });
}

function createCell(className = "") {
    const cell = document.createElement("td");
    cell.className = className;
    return cell;
}

function createRequestRow(request) {
    const review = getReview(request);
    const row = document.createElement("tr");

    const selectCell = createCell("select-cell");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = selectedRequestIds.has(request.id);
    checkbox.setAttribute("aria-label", `Select ${request.name}`);
    checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
            selectedRequestIds.add(request.id);
        } else {
            selectedRequestIds.delete(request.id);
        }
        updateSelectionSummary();
        renderHeaders();
    });
    selectCell.append(checkbox);
    row.append(selectCell);

    const nameCell = createCell("request-name");
    nameCell.textContent = request.name;
    row.append(nameCell);

    const descriptionCell = createCell("description");
    descriptionCell.textContent = request.description;
    row.append(descriptionCell);

    const areaCell = createCell("area");
    areaCell.textContent = request.area;
    row.append(areaCell);

    const requesterCell = createCell("requester");
    requesterCell.append(document.createTextNode(`${request.requester || "Unknown"} `));
    const links = document.createElement("span");
    links.className = "link-list";
    links.append(createLink("Ask", request.message_url));
    if (request.completion_url) {
        links.append(createLink("Completion evidence", request.completion_url));
    }
    requesterCell.append(links);
    row.append(requesterCell);

    const completedCell = createCell();
    completedCell.append(createBadge(request.completed));
    row.append(completedCell);

    const existingCell = createCell();
    existingCell.append(createBadge(request.existing));
    row.append(existingCell);

    const confidenceCell = createCell();
    confidenceCell.textContent = request.match_confidence || "unknown";
    row.append(confidenceCell);

    const relatedCell = createCell("related");
    if (request.related_url) {
        relatedCell.append(createLink(request.related_name, request.related_url));
    } else {
        const newRequest = document.createElement("span");
        newRequest.className = "new-request";
        newRequest.textContent = `[NEW] ${request.related_name}`;
        relatedCell.append(newRequest);
    }
    row.append(relatedCell);

    const reviewCell = createCell("review");
    const reviewSelect = document.createElement("select");
    reviewSelect.setAttribute("aria-label", `Review status for ${request.name}`);
    for (const [value, label] of reviewOptions) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        option.selected = review.reviewStatus === value;
        reviewSelect.append(option);
    }
    reviewSelect.addEventListener("change", () => saveReview(request, { reviewStatus: reviewSelect.value }));
    reviewCell.append(reviewSelect);
    row.append(reviewCell);

    const notesCell = createCell("notes");
    const notes = document.createElement("textarea");
    notes.value = review.notes;
    notes.placeholder = "Add context, a decision, or a next step";
    notes.setAttribute("aria-label", `Notes for ${request.name}`);
    notes.addEventListener("input", () => saveReview(request, { notes: notes.value }));
    notesCell.append(notes);
    row.append(notesCell);

    return row;
}

function toggleVisibleRequests(checked) {
    for (const request of filterRequests()) {
        if (checked) {
            selectedRequestIds.add(request.id);
        } else {
            selectedRequestIds.delete(request.id);
        }
    }
    renderTable();
}

function renderHeaders() {
    elements.headers.replaceChildren();
    const visibleRequests = filterRequests();
    const selectedVisibleCount = visibleRequests.filter((request) => selectedRequestIds.has(request.id)).length;
    const selectionHeader = document.createElement("th");
    selectionHeader.className = "select-cell";
    const selectAll = document.createElement("input");
    selectAll.type = "checkbox";
    selectAll.checked = visibleRequests.length > 0 && selectedVisibleCount === visibleRequests.length;
    selectAll.indeterminate = selectedVisibleCount > 0 && selectedVisibleCount < visibleRequests.length;
    selectAll.setAttribute("aria-label", "Select all visible requests");
    selectAll.addEventListener("change", () => toggleVisibleRequests(selectAll.checked));
    selectionHeader.append(selectAll);
    elements.headers.append(selectionHeader);

    for (const [key, label, className] of columns) {
        const header = document.createElement("th");
        header.className = className;
        header.setAttribute("aria-sort", sortKey === key ? (sortDirection === "asc" ? "ascending" : "descending") : "none");
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = `${label}${sortKey === key ? (sortDirection === "asc" ? " ↑" : " ↓") : ""}`;
        button.addEventListener("click", () => {
            if (sortKey === key) {
                sortDirection = sortDirection === "asc" ? "desc" : "asc";
            } else {
                sortKey = key;
                sortDirection = "asc";
            }
            renderTable();
        });
        header.append(button);
        elements.headers.append(header);
    }
}

function renderTable() {
    const requests = filterRequests().sort(compareRequests);
    elements.body.replaceChildren(...requests.map(createRequestRow));
    elements.empty.hidden = requests.length > 0;
    elements.summary.textContent = `${requests.length} of ${requestRows.length} requests shown`;
    renderHeaders();
    updateSelectionSummary();
}

function updateSelectionSummary() {
    const count = selectedRequestIds.size;
    elements.selectionSummary.textContent = `${count} selected`;
    elements.applyBulkStatus.disabled = count === 0 || !elements.bulkStatus.value;
    elements.clearSelection.disabled = count === 0;
}

function updateReviewSummary() {
    const reviewedCount = requestRows.filter((request) => getReview(request).reviewStatus !== "unreviewed").length;
    const notedCount = requestRows.filter((request) => getReview(request).notes.trim()).length;
    elements.status.textContent = `${reviewedCount} reviewed. ${notedCount} have notes. Saved locally.`;
}

function resetFilters() {
    elements.search.value = "";
    elements.area.value = "";
    elements.completed.value = "";
    elements.existing.value = "";
    elements.confidence.value = "";
    elements.review.value = "";
    renderTable();
}

function applyBulkStatus() {
    const reviewStatus = elements.bulkStatus.value;
    if (!reviewStatus || selectedRequestIds.size === 0) {
        return;
    }
    const updatedAt = new Date().toISOString();
    for (const request of requestRows) {
        if (selectedRequestIds.has(request.id)) {
            reviews[request.id] = { ...getReview(request), reviewStatus, updatedAt };
        }
    }
    const changedCount = selectedRequestIds.size;
    saveReviews(`Updated ${changedCount} requests.`);
    renderTable();
}

function clearSelection() {
    selectedRequestIds.clear();
    renderTable();
}

function getReviewExport() {
    return {
        format: "slack-request-review",
        version: 1,
        metadata,
        exportedAt: new Date().toISOString(),
        reviews,
    };
}

function exportReview() {
    const blob = new Blob([JSON.stringify(getReviewExport(), null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "slack-request-review.json";
    link.click();
    URL.revokeObjectURL(url);
    elements.status.textContent = "Review exported.";
}

async function copyReviewSummary() {
    const reviewed = requestRows.filter((request) => {
        const review = getReview(request);
        return review.reviewStatus !== "unreviewed" || review.notes.trim();
    });
    if (!reviewed.length) {
        elements.status.textContent = "Add a note or change a review status before copying.";
        return;
    }
    const lines = reviewed.flatMap((request) => {
        const review = getReview(request);
        const label = reviewOptions.find(([value]) => value === review.reviewStatus)?.[1] || review.reviewStatus;
        const related = request.related_url ? `Feature request: ${request.related_url}` : `Proposed request: ${request.related_name}`;
        return [`## ${request.name}`, `Review status: ${label}`, `Notes: ${review.notes.trim() || "None"}`, `Slack ask: ${request.message_url}`, related, ""];
    });
    try {
        await navigator.clipboard.writeText(lines.join("\n"));
        elements.status.textContent = `Copied ${reviewed.length} reviewed requests.`;
    } catch {
        elements.status.textContent = "Could not copy the review. Export it instead.";
    }
}

async function importReview(file) {
    try {
        const imported = JSON.parse(await file.text());
        if (imported.format !== "slack-request-review" || typeof imported.reviews !== "object") {
            throw new Error("invalid format");
        }
        reviews = { ...reviews, ...imported.reviews };
        saveReviews("Review imported and saved locally.");
        renderTable();
    } catch {
        elements.status.textContent = "Could not import this file. Choose a review JSON file exported from this page.";
    }
}

for (const area of areaOrder) {
    const option = document.createElement("option");
    option.value = area;
    option.textContent = area;
    elements.area.append(option);
}

for (const element of [elements.area, elements.completed, elements.existing, elements.confidence, elements.review]) {
    element.addEventListener("change", renderTable);
}
elements.search.addEventListener("input", renderTable);
elements.bulkStatus.addEventListener("change", updateSelectionSummary);
elements.applyBulkStatus.addEventListener("click", applyBulkStatus);
elements.clearSelection.addEventListener("click", clearSelection);
document.querySelector("#reset-filters").addEventListener("click", resetFilters);
document.querySelector("#export-review").addEventListener("click", exportReview);
document.querySelector("#copy-review").addEventListener("click", copyReviewSummary);
document.querySelector("#import-review").addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) {
        importReview(file);
    }
    event.target.value = "";
});

renderTable();
updateReviewSummary();
</script>
</body>
</html>
'''
    return (
        template.replace("__TITLE__", title)
        .replace("__REQUEST_DATA__", payload)
        .replace("__METADATA__", metadata)
    )


def main() -> None:
    args = parse_args()
    data = parse_review_data(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(create_html(data))
    print(f"Created {args.output} with {len(data['requests'])} requests")


if __name__ == "__main__":
    main()
