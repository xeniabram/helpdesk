import type { Ticket, TicketStatus } from "./types";

const API_BASE = "/api";

export async function fetchTickets(status?: TicketStatus): Promise<Ticket[]> {
  const params = status ? `?status=${status}` : "";
  const res = await fetch(`${API_BASE}/tickets${params}`);
  if (!res.ok) throw new Error("Failed to fetch tickets");
  return res.json();
}

export async function fetchTicket(id: number): Promise<Ticket> {
  const res = await fetch(`${API_BASE}/tickets/${id}`);
  if (!res.ok) throw new Error("Ticket not found");
  return res.json();
}

export function createSummaryEventSource(ticketId: number): EventSource {
  return new EventSource(`${API_BASE}/tickets/${ticketId}/summary`);
}
