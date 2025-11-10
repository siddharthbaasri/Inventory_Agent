"use client";
import { useState, useRef, useEffect } from "react";

type Role = "user" | "assistant";
type Message = { role: Role; content: string };
const SERVER_URL = "http://127.0.0.1:8080/api/chat"

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    setInput("");

    const userMessage: Message = {role: "user", content: input}
    setMessages((prev) => [...prev, userMessage]);
    let serverMessage = ""
    try {
      const res = await fetch(SERVER_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json", 
        },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();
      serverMessage = data.reply;
    }
    catch {
      serverMessage = "There was an issue in connecting to the server";
    }
    finally {
      const botMsg: Message = { role: "assistant", content: serverMessage };
      setMessages((prev) => [...prev, botMsg]);
    }
  };

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      {/* Left pane */}
      <div className="w-72 bg-gray-100 overflow-y-auto">
      </div>

      {/* Right pane */}
      <div className="flex-1 overflow-y-auto bg-white">

        {
           messages.map((msg, i) => {
            return <div> {msg.content} </div>
           })
        }

        {/* Bottom box */}
        <div className="fixed bottom-0 left-0 right-0 flex justify-center px-4 py-4 bg-gradient-to-t from-[#f7f7f8] via-[#f7f7f8]/90 pointer-events-none">
          <div className="w-full max-w-3xl flex gap-2 pointer-events-auto">
            <textarea
              ref={textareaRef}
              className="flex-1 bg-white border border-gray-300 rounded-xl p-3 text-[15px] shadow-sm focus:outline-none resize-none"
              placeholder="Message..."
              value={input}
              rows={1}
              onChange={handleTextareaChange}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              style={{ minHeight: "44px", maxHeight: "200px", overflowY: textareaRef.current && textareaRef.current.scrollHeight > 200 ? 'auto' : 'hidden' }}
            />

            <button
              className="px-5 rounded-xl bg-black text-white font-medium hover:opacity-80 transition"
              onClick={sendMessage}
              style={{ height: "44px", minHeight: "44px" }}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
