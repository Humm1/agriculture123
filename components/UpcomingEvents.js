import React, { useEffect, useState } from "react";
import { View, Text, FlatList } from "react-native";
import { fetchUserUpcomingEvents } from "../api";


export function UpcomingEvents({ userId }) {
  const [events, setEvents] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("UpcomingEvents - Received userId:", userId);
    
    if (!userId) {
      setError("No user found. Please log in to view upcoming events.");
      setEvents(null);
      return;
    }
    setError(null);
    console.log("UpcomingEvents - Fetching events for userId:", userId);
    
    fetchUserUpcomingEvents(userId)
      .then(data => {
        console.log("UpcomingEvents - Data received:", data);
        if (!data || !data.success || !data.events_by_date) {
          setError("No upcoming events found.");
          setEvents(null);
        } else {
          setEvents(data);
        }
      })
      .catch((err) => {
        console.error("UpcomingEvents - Error:", err);
        setError("Failed to load upcoming events. Please try again later.");
        setEvents(null);
      });
  }, [userId]);

  if (error) return <Text style={{ color: 'red', margin: 10 }}>{error}</Text>;
  if (!events) return <Text>Loading...</Text>;

  const allEmpty = Object.values(events.events_by_date).every(arr => arr.length === 0);
  if (allEmpty) return <Text style={{ margin: 10 }}>No upcoming events scheduled.</Text>;

  return (
    <View>
      <Text style={{ fontSize: 20, fontWeight: "bold" }}>Upcoming Farm Events</Text>
      {Object.entries(events.events_by_date).map(([date, evs]) => (
        evs.length > 0 && (
          <View key={date}>
            <Text style={{ fontWeight: "600", marginTop: 10 }}>{date}</Text>
            <FlatList
              data={evs}
              keyExtractor={item => item.id}
              renderItem={({ item }) => (
                <View style={{ marginVertical: 3 }}>
                  <Text>
                    <Text style={{ fontWeight: "bold" }}>{item.practice_name}</Text> ({item.status})
                    {item.digital_plots?.plot_name ? ` — ${item.digital_plots.plot_name}` : ""}
                  </Text>
                </View>
              )}
            />
          </View>
        )
      ))}
    </View>
  );
}
