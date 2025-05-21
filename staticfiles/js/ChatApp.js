import React, { useState, useEffect } from "react";
import { connectWebSocket, sendMessage } from "./websocket";

const ChatApp = ({ roomName, username }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState("");

    useEffect(() => {
        const socket = connectWebSocket(roomName, (message) => {
            setMessages((prevMessages) => [...prevMessages, message]);
        });

        return () => socket.close();  // Close WebSocket when component unmounts
    }, [roomName]);

    const handleSendMessage = () => {
        if (newMessage.trim() !== "") {
            sendMessage(roomName, { username, message: newMessage });
            setNewMessage("");
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div key={index} className="chat-message">
                        <strong>{msg.username}: </strong>{msg.message}
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                />
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
};

export default ChatApp;
