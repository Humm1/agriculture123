import React, { useState } from "react";
import { Button, TextInput, View } from "react-native";
import { completeEvent, rescheduleEvent, createCustomEvent } from "../api";

export function EventActions({ eventId, plotId, userId }) {
  const [notes, setNotes] = useState("");
  const [hours, setHours] = useState("");
  const [newDate, setNewDate] = useState("");
  const [customName, setCustomName] = useState("");

  return (
    <View>
      <TextInput placeholder="Completion notes" value={notes} onChangeText={setNotes} />
      <TextInput placeholder="Labor hours" value={hours} onChangeText={setHours} keyboardType="numeric" />
      <Button title="Complete Event" onPress={() => completeEvent(eventId, notes, hours, [])} />

      <TextInput placeholder="New date (YYYY-MM-DD)" value={newDate} onChangeText={setNewDate} />
      <Button title="Reschedule Event" onPress={() => rescheduleEvent(eventId, newDate, "User rescheduled")} />

      <TextInput placeholder="Custom Event Name" value={customName} onChangeText={setCustomName} />
      <Button
        title="Create Custom Event"
        onPress={() =>
          createCustomEvent({
            plotId,
            userId,
            practiceName: customName,
            scheduledDate: newDate,
            description: "User custom event",
            priority: "moderate"
          })
        }
      />
    </View>
  );
}
