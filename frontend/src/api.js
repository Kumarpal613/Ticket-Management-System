
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function describeError(body, status) {
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    // FastAPI validation errors: [{ loc: ["body", "title"], msg: "..." }]
    return detail.map((d) => `${d.loc.slice(1).join(".")}: ${d.msg}`).join("; ");
  }
  return `Request failed (${status})`;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error(`Cannot reach the server at ${BASE_URL}. Is the backend running?`);
  }
  if (response.status === 204) return null;
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(describeError(body, response.status));
  return body;
}

export const api = {
  listTickets: (status) =>
    request(status ? `/tickets?status=${encodeURIComponent(status)}` : "/tickets"),
  getSummary: () => request("/tickets/summary"),
  createTicket: (payload) =>
    request("/tickets", { method: "POST", body: JSON.stringify(payload) }),
  updateTicket: (id, changes) =>
    request(`/tickets/${id}`, { method: "PATCH", body: JSON.stringify(changes) }),
  deleteTicket: (id) => request(`/tickets/${id}`, { method: "DELETE" }),
};

export const STATUSES = ["Open", "In Progress", "Resolved"];
export const PRIORITIES = ["Low", "Medium", "High"];
