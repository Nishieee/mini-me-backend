const { contextBridge } = require('electron');

let socket;
let messageHandlers = [];

function connectWebSocket() {
  try {
    socket = new WebSocket('ws://localhost:8081');

    socket.onopen = () => {
      console.log('✅ Connected to MiniMe backend WebSocket');
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      console.log('Disconnected from MiniMe backend WebSocket');
      // Attempt to reconnect after 2 seconds
      setTimeout(() => {
        connectWebSocket();
      }, 2000);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        messageHandlers.forEach(handler => {
          try {
            handler(data);
          } catch (e) {
            console.error('Error in message handler:', e);
          }
        });
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
      }
    };
  } catch (e) {
    console.error('Failed to create WebSocket:', e);
    // Retry after 2 seconds
    setTimeout(() => {
      connectWebSocket();
    }, 2000);
  }
}

// Start connection
connectWebSocket();

// Expose MiniMeSocket API to renderer
contextBridge.exposeInMainWorld('MiniMeSocket', {
  onMessage: (callback) => {
    if (typeof callback === 'function') {
      messageHandlers.push(callback);
    }
  },
  send: (data) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, cannot send:', data);
    }
  },
  isConnected: () => socket && socket.readyState === WebSocket.OPEN
});

