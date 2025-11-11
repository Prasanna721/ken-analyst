"use client";

import { useState, useRef, useEffect } from "react";

interface ChunkDetailPanelProps {
  chunk: any;
  workspaceId: string;
  onClose: () => void;
}

export default function ChunkDetailPanel({ chunk, workspaceId, onClose }: ChunkDetailPanelProps) {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [inputValue, setInputValue] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [agentId, setAgentId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isStreaming) return;

    const userMessage = inputValue.trim();
    setInputValue("");

    // Add user message to UI
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setIsStreaming(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/agent/query/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          workspace_id: workspaceId,
          agent_id: agentId,
          prompt: userMessage,
          chunk_id: chunk.id,
          chunk_content: chunk.markdown
        })
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      let assistantMessage = "";
      setMessages(prev => [...prev, { role: "assistant", content: "" }]);

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = JSON.parse(line.slice(6));

              if (data.type === "agent_id") {
                setAgentId(data.agent_id);
              } else if (data.type === "text") {
                assistantMessage += data.content;
                setMessages(prev => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    role: "assistant",
                    content: assistantMessage
                  };
                  return newMessages;
                });
              } else if (data.type === "done") {
                setIsStreaming(false);
              } else if (data.type === "error") {
                setMessages(prev => [...prev, { role: "error", content: data.content }]);
                setIsStreaming(false);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages(prev => [...prev, { role: "error", content: "Failed to send message" }]);
      setIsStreaming(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Show full chat view if messages exist
  if (messages.length > 0) {
    return (
      <div className="border-l border-border flex flex-col bg-background-primary h-full">
        {/* Header */}
        <div className="border-b border-border p-4 flex justify-between items-center">
          <h3 className="font-medium text-text-primary">Chat with Analyst Ken</h3>
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-text-primary"
          >
            ✕
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] p-3 text-sm ${
                  msg.role === "user"
                    ? "bg-golden-light text-text-primary"
                    : msg.role === "error"
                    ? "bg-red-100 text-red-600"
                    : "bg-background-secondary text-text-primary"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-border p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about this chunk..."
              disabled={isStreaming}
              className="flex-1 px-3 py-2 text-sm border border-border bg-background-primary text-text-primary placeholder-text-secondary focus:outline-none focus:border-golden"
            />
            <button
              onClick={handleSendMessage}
              disabled={isStreaming || !inputValue.trim()}
              className="px-4 py-2 text-sm bg-golden text-white hover:opacity-80 disabled:opacity-30 transition-opacity"
            >
              {isStreaming ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show chunk details view with button
  return (
    <div className="border-l border-border flex flex-col bg-background-primary h-full">
      {/* Header */}
      <div className="border-b border-border p-4 flex justify-between items-center">
        <h3 className="font-medium text-text-primary">Chunk Details</h3>
        <button
          onClick={onClose}
          className="text-text-secondary hover:text-text-primary"
        >
          ✕
        </button>
      </div>

      {/* Chunk Info */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-4 text-sm">
          <div>
            <div className="font-medium text-text-secondary mb-2 text-xs uppercase tracking-wide">Chunk ID</div>
            <div className="text-text-primary font-mono text-xs break-all bg-background-secondary p-2">{chunk.id}</div>
          </div>
          <div>
            <div className="font-medium text-text-secondary mb-2 text-xs uppercase tracking-wide">Content</div>
            <div
              className="text-text-primary text-xs chunk-content"
              dangerouslySetInnerHTML={{ __html: chunk.markdown }}
            />
          </div>
        </div>
      </div>

      {/* Spin Analyst Ken Button */}
      <div className="border-t border-border p-6">
        <h2 className="font-heading text-xl text-text-primary mb-3">Spin Analyst Ken</h2>
        <button
          className="w-full px-6 py-3 text-sm font-medium text-golden hover:bg-golden-light transition-all border border-golden"
          style={{ opacity: 0.3 }}
          onMouseEnter={(e) => e.currentTarget.style.opacity = "1"}
          onMouseLeave={(e) => e.currentTarget.style.opacity = "0.3"}
          onClick={() => {
            setMessages([{ role: "assistant", content: "Hello! I'm Analyst Ken. How can I help you analyze this content?" }]);
          }}
        >
          Start Analysis
        </button>
      </div>
    </div>
  );
}
