import React from "react";
import { ScrollView } from "react-native";
import { PlotCalendar } from "./components/PlotCalendar";
import { UpcomingEvents } from "./components/UpcomingEvents";

export default function Dashboard({ selectedPlotId, currentUserId }) {
  console.log("Dashboard - Received props:", { selectedPlotId, currentUserId });
  
  return (
    <ScrollView>
      <PlotCalendar plotId={selectedPlotId} />
      <UpcomingEvents userId={currentUserId} />
    </ScrollView>
  );
}
