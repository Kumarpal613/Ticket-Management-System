import { useCallback, useEffect, useState } from "react";
import { api, STATUSES } from "./api.js";
import SummaryBar from "./components/SummaryBar.jsx";
import TicketForm from "./components/TicketForm.jsx";
import TicketTable from "./components/TicketTable.jsx";

export default function App() {
  const [tickets, setTickets] = useState([]);
  const [summary, setSummary] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Reload the list AND the summary so both always match the database.
  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [list, stats] = await Promise.all([
        api.listTickets(statusFilter),
        api.getSummary(),
      ]);
      setTickets(list);
      setSummary(stats);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function handleCreate(payload) {
    await api.createTicket(payload); // errors are shown by the form itself
    await refresh();
  }

  async function handleStatusChange(id, status) {
    try {
      await api.updateTicket(id, { status });
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this ticket? This cannot be undone.")) return;
    try {
      await api.deleteTicket(id);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="page">
      <h1>Support tickets</h1>

      <SummaryBar summary={summary} />
      <TicketForm onCreate={handleCreate} />

      <section>
        <div className="toolbar">
          <h2>All tickets</h2>
          <label>
            Filter by status{" "}
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
        </div>

        {error && <p className="message error" role="alert">{error}</p>}
        {loading && <p className="message">Loading tickets…</p>}
        {!loading && !error && tickets.length === 0 && (
          <p className="message">
            {statusFilter ? `No tickets with status "${statusFilter}".` : "No tickets yet. Create the first one above."}
          </p>
        )}
        {tickets.length > 0 && (
          <TicketTable
            tickets={tickets}
            onStatusChange={handleStatusChange}
            onDelete={handleDelete}
          />
        )}
      </section>
    </main>
  );
}
