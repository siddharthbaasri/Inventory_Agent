"use client";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Role = "user" | "assistant";
type Message = { role: Role; content: string };
const SERVER_URL = "http://127.0.0.1:8080/api/chat"

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
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
    setIsLoading(true);

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
      console.log(serverMessage)
    }
    catch {
      serverMessage = "There was an issue in connecting to the server";
    }
    finally {
      setIsLoading(false);
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
      <div className="flex-1 pt-4 overflow-y-auto bg-white">

        {
           messages.map((msg, i) => {
            return <div key={i} className="w-full flex justify-center px-4"> 
             {/* Message text */}
              <div className={`w-full max-w-3xl flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-3xl w-fit text-[15px] ${
                    msg.role === "user"
                      ? "bg-gray-200 text-black px-4 py-3 rounded-xl whitespace-pre-space"
                      : "px-4 py-3 rounded-xl"
                  }`}
                >
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    skipHtml={false}
                    components={{
                      p: ({node, ...props}) => <p className="mb-2" {...props} />,
                      h3: ({node, ...props}) => <h3 className="mt-4 mb-2" {...props} />,
                      ul: ({node, ...props}) => <ul className="mt-1 mb-2" {...props} />,
                      li: ({node, ...props}) => <li className="mb-1" {...props} />,
                      strong: ({node, ...props}) => <strong className="break-words" {...props} />
                    }}
                  >
                    {msg.content} 
                  </ReactMarkdown>
                </div>
              </div>
            </div>
           })
        }

        {/* Typing Indicator */}
        {isLoading && (
          <div className="w-full flex justify-center px-4 mb-2">
            <div className="w-full max-w-3xl flex gap-3 justify-start">
              <div className="bg-white border border-gray-300 px-4 py-3 rounded-xl">
                <div className="flex gap-1">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Bottom box */}
        <div className="fixed bottom-0 left-72 right-0 flex justify-center px-4 py-4 bg-gradient-to-t from-[#f7f7f8] via-[#f7f7f8]/90 pointer-events-none">
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
