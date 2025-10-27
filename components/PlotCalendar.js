import React, { useEffect, useState } from "react";
import { View, Text, FlatList, StyleSheet } from "react-native";
import { fetchPlotCalendar } from "../api";


export function PlotCalendar({ plotId }) {
  const [calendar, setCalendar] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("PlotCalendar - Received plotId:", plotId);
    
    if (!plotId) {
      setError("No plot selected. Please select a plot to view the calendar.");
      setCalendar(null);
      return;
    }
    setError(null);
    console.log("PlotCalendar - Fetching calendar for plotId:", plotId);
    
    fetchPlotCalendar(plotId)
      .then(data => {
        console.log("PlotCalendar - Data received:", data);
        if (!data || !data.success || !data.grouped_events) {
          setError("No calendar data found for this plot.");
          setCalendar(null);
        } else {
          setCalendar(data);
        }
      })
      .catch((err) => {
        console.error("PlotCalendar - Error:", err);
        setError("Failed to load calendar data. Please try again later.");
        setCalendar(null);
      });
  }, [plotId]);

  if (error) return <Text style={{ color: 'red', margin: 10 }}>{error}</Text>;
  if (!calendar) return <Text>Loading...</Text>;

  // Check if all event groups are empty
  const allEmpty = Object.values(calendar.grouped_events).every(arr => arr.length === 0);
  if (allEmpty) return <Text style={{ margin: 10 }}>No scheduled events for this plot.</Text>;

  return (
    <View>
      <Text style={styles.header}>Farm Calendar</Text>
      {Object.entries(calendar.grouped_events).map(([type, events]) => (
        events.length > 0 && (
          <View key={type}>
            <Text style={styles.subheader}>{type.replace("_", " ").toUpperCase()}</Text>
            <FlatList
              data={events}
              keyExtractor={item => item.id}
              renderItem={({ item }) => (
                <View style={styles.eventCard}>
                  <Text style={styles.eventTitle}>{item.practice_name}</Text>
                  <Text>Date: {new Date(item.scheduled_date).toLocaleDateString()}</Text>
                  <Text>Status: {item.status}</Text>
                  <Text>{item.description}</Text>
                </View>
              )}
            />
          </View>
        )
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  header: { fontSize: 22, fontWeight: "bold", marginVertical: 10 },
  subheader: { fontSize: 18, fontWeight: "600", marginTop: 10 },
  eventCard: { backgroundColor: "#f0f0f0", marginVertical: 5, padding: 10, borderRadius: 8 },
  eventTitle: { fontWeight: "bold" }
});
