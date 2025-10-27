import { useEffect, useState } from "react";

const API_BASE = "https://urchin-app-86rjy.ondigitalocean.app/api/advanced-growth";

export async function fetchUserPlots(userId) {
  try {
    console.log(`Fetching plots for user: ${userId}`);
    console.log(`URL: ${API_BASE}/plots/user/${userId}`);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const res = await fetch(`${API_BASE}/plots/user/${userId}`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    
    console.log(`Response status: ${res.status}`);
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const data = await res.json();
    console.log('Response data:', data);
    
    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('⏱️  Request timeout - backend is not responding');
      return { success: false, error: 'timeout', plots: [], message: 'Backend not responding' };
    }
    console.error('Error fetching plots:', error);
    throw error;
  }
}
