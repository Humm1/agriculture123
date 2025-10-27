const API_BASE = "https://urchin-app-86rjy.ondigitalocean.app/api/advanced-growth";

export async function fetchPlotCalendar(plotId) {
  const res = await fetch(`${API_BASE}/calendar/${plotId}`);
  return res.json();
}

export async function fetchUserUpcomingEvents(userId, daysAhead = 14) {
  const res = await fetch(`${API_BASE}/calendar/user/${userId}/upcoming?days_ahead=${daysAhead}`);
  return res.json();
}

export async function completeEvent(eventId, notes, hours, images) {
  const res = await fetch(`${API_BASE}/calendar/event/${eventId}/complete`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      completion_notes: notes,
      actual_labor_hours: hours,
      completion_images: images
    })
  });
  return res.json();
}

export async function rescheduleEvent(eventId, newDate, reason) {
  const res = await fetch(`${API_BASE}/calendar/event/${eventId}/reschedule`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ new_date: newDate, reason })
  });
  return res.json();
}

export async function createCustomEvent({ plotId, userId, practiceName, scheduledDate, description, priority }) {
  const res = await fetch(`${API_BASE}/calendar/event/custom`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      plot_id: plotId,
      user_id: userId,
      practice_name: practiceName,
      scheduled_date: scheduledDate,
      description,
      priority
    })
  });
  return res.json();
}
