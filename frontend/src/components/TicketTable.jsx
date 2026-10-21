import { STATUSES } from "../api.js";

// The backend sends UTC times without a "Z", so add it before parsing.
function formatDate(iso) {
  return new Date(iso + "Z").toLocaleString();
}

export default function TicketTable({ tickets, onStatusChange, onDelete }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr key={ticket.id}>
              <td>{ticket.id}</td>
              <td>
                <div>{ticket.title}</div>
                {ticket.description && <small>{ticket.description}</small>}
              </td>
              <td>{ticket.priority}</td>
              <td>
                <select
                  value={ticket.status}
                  aria-label={`Status of ticket ${ticket.id}`}
                  onChange={(e) => onStatusChange(ticket.id, e.target.value)}
                >
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </td>
              <td>{formatDate(ticket.created_at)}</td>
              <td>
                <button className="link-danger" onClick={() => onDelete(ticket.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
