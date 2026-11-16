import React, { useState } from "react";
import {
  Bot,
  Copy,
  FileText,
  Lightbulb,
  MessageSquare,
  Send,
  Sparkles,
  User,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { Badge } from "@/components/ui/badge";

interface Message {
  id: string;
  sender: "user" | "copilot";
  text: string;
  timestamp: string;
}

export function AICopilotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "copilot",
      text: "Hello! I am your NexusMind Cloud Operations Copilot. In Phase 1, I am operating in Architectural Foundation mode. You can test prompt routing and structured report generation queries.",
      timestamp: "12:00 PM",
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");

  const suggestedPrompts = [
    "Analyze peak CPU utilization patterns in our cluster trace.",
    "Recommend right-sizing actions for underutilized EC2 nodes.",
    "Generate an executive cloud cost optimization report.",
    "Forecast compute demand for upcoming traffic surge.",
  ];

  const handleSend = (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim()) return;

    const userMsg: Message = {
      id: String(Date.now()),
      sender: "user",
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMessage("");

    // Phase 1 response explaining architectural readiness
    setTimeout(() => {
      const copilotMsg: Message = {
        id: String(Date.now() + 1),
        sender: "copilot",
        text: `[Phase 1 Copilot Foundation]: Query received: "${text.trim()}". The conversational agent pipeline, RAG vector retrieval, and LLM generative synthesis will be fully connected in Phase 6. Telemetry and statistical features are currently accessible via the Analytics and Datasets modules.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, copilotMsg]);
    }, 600);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="GenAI Cloud Operations Copilot"
        description="Conversational infrastructure assistant for automated incident analysis, demand forecasting queries, and executive reports."
      >
        <Badge variant="secondary" className="text-xs">
          Phase 1 Foundation Mode
        </Badge>
      </PageHeader>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[600px]">
        {/* Left: Suggested Prompts & Tools */}
        <Card className="lg:col-span-1 border-border flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-amber-500" />
              Suggested Queries
            </CardTitle>
            <CardDescription className="text-xs">
              Quick prompts to explore platform intelligence
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 overflow-y-auto flex-1">
            {suggestedPrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(p)}
                className="w-full text-left p-2.5 rounded-lg border border-border bg-card hover:bg-accent text-xs text-muted-foreground hover:text-foreground transition-all flex items-start gap-2 group"
              >
                <Sparkles className="w-3.5 h-3.5 text-primary mt-0.5 flex-shrink-0 group-hover:scale-110 transition-transform" />
                <span>{p}</span>
              </button>
            ))}
          </CardContent>
        </Card>

        {/* Right: Chat Feed */}
        <Card className="lg:col-span-3 border-border flex flex-col overflow-hidden">
          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex items-start gap-3 text-xs ${
                  m.sender === "user" ? "flex-row-reverse" : ""
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                    m.sender === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                  }`}
                >
                  {m.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div
                  className={`max-w-[80%] rounded-xl p-3.5 space-y-1 ${
                    m.sender === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted/50 border border-border text-foreground"
                  }`}
                >
                  <p className="leading-relaxed whitespace-pre-wrap">{m.text}</p>
                  <span
                    className={`block text-[10px] ${
                      m.sender === "user" ? "text-primary-foreground/70" : "text-muted-foreground"
                    }`}
                  >
                    {m.timestamp}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Input Bar */}
          <div className="p-3 border-t border-border bg-card/80">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <Input
                type="text"
                placeholder="Ask NexusMind Copilot about cloud workloads or demand forecasts..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                className="h-10 text-xs"
              />
              <Button type="submit" size="sm" className="h-10 px-4">
                <Send className="w-4 h-4" />
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </div>
  );
}

