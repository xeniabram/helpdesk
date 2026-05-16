import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { createSummaryEventSource, fetchTicket } from "../api";
import { StatusBadge } from "../components/StatusBadge";
import type { Ticket } from "../types";

export function TicketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [waitingForFirstToken, setWaitingForFirstToken] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  useEffect(() => {
    fetchTicket(Number(id))
      .then(setTicket)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  function handleGenerateSummary() {
    setSummary("");
    setSummaryError(null);
    setSummaryLoading(true);
    setWaitingForFirstToken(true);

    const es = createSummaryEventSource(Number(id));

    es.onmessage = (event) => {
      setWaitingForFirstToken(false);
      const data = JSON.parse(event.data);
      setSummary((prev) => prev + data.content);
    };

    es.addEventListener("done", () => {
      setSummaryLoading(false);
      es.close();
    });

    es.addEventListener("error", (event) => {
      const messageEvent = event as MessageEvent;
      if (messageEvent.data) {
        const data = JSON.parse(messageEvent.data);
        setSummaryError(data.error);
      } else {
        setSummaryError("Connection to server lost");
      }
      setSummaryLoading(false);
      setWaitingForFirstToken(false);
      es.close();
    });
  }

  if (loading) return <p>Loading...</p>;
  if (error || !ticket)
    return (
      <div>
        <Link to="/">&larr; Back to tickets</Link>
        <p className="error">{error || "Ticket not found"}</p>
      </div>
    );

  return (
    <div>
      <Link to="/">&larr; Back to tickets</Link>

      <h1>{ticket.title}</h1>

      <div className="ticket-meta">
        <StatusBadge status={ticket.status} />
        <span>Created: {new Date(ticket.created_at).toLocaleString()}</span>
      </div>

      <div className="ticket-description">
        <h2>Description</h2>
        <p>{ticket.description}</p>
      </div>

      <div className="ticket-summary">
        <h2>AI Summary</h2>
        <button onClick={handleGenerateSummary} disabled={summaryLoading}>
          {summaryLoading ? "Generating..." : "Generate Summary"}
        </button>

        {waitingForFirstToken && (
          <div className="summary-text">
            <span className="dots" />
          </div>
        )}

        {summary && (
          <div className="summary-text">
            {summary}
          </div>
        )}

        {summaryError && <p className="error">{summaryError}</p>}
      </div>
    </div>
  );
}
