export default function SummaryBar({ summary }) {
  if (!summary) return null;
  const oldest = summary.oldest_unresolved;
  return (
    <section className="summary" aria-label="Ticket summary">
      <div><strong>{summary.total}</strong> total</div>
      <div><strong>{summary.open}</strong> open</div>
      <div><strong>{summary.in_progress}</strong> in progress</div>
      <div><strong>{summary.resolved}</strong> resolved</div>
      <div><strong>{summary.high_priority}</strong> high priority</div>
      <div className="oldest">
        Oldest unresolved:{" "}
        {oldest ? `#${oldest.id} ${oldest.title}` : "none"}
      </div>
    </section>
  );
}
