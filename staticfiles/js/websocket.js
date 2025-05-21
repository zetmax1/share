// import React from "react";
// import ReactDOM from "react-dom";
// import ChatApp from "./ChatApp";
// import "./styles.css";

// // Find the HTML element where React will be rendered
// const chatContainer = document.getElementById("chat-root");

// if (chatContainer) {
//   ReactDOM.render(<ChatApp />, chatContainer);
// } else {
//   console.error("Chat root element not found! Make sure you have <div id='chat-root'></div> in your template.");
// }

let socket = null;

export const connectWebSocket = (roomName, onMessageReceived) => {
    socket = new WebSocket(`ws://localhost:8000/ws/chat/${roomName}/`);

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessageReceived(data);
    };

    socket.onclose = () => {
        console.log("WebSocket closed");
    };

    return socket;
};

export const sendMessage = (roomName, message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(message));
    } else {
        console.error("WebSocket not connected");
    }
};
