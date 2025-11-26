"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Send, Loader2, Database, Code, CheckCircle, XCircle } from "lucide-react";
import apiClient from "@/lib/api-client";

interface Connection {
    id: number;
    name: string;
    type: string;
}

interface Message {
    role: "user" | "assistant";
    content: string;
    sql?: string;
    explanation?: string;
    execution?: {
        success: boolean;
        columns: string[];
        rows: any[];
        row_count: number;
        error?: string;
    };
}

export default function ChatPage() {
    const [connections, setConnections] = useState<Connection[]>([]);
    const [selectedConnection, setSelectedConnection] = useState<number | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState<number | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetchConnections();
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const fetchConnections = async () => {
        try {
            const data = await apiClient.connections.list();
            setConnections(data);
            if (data.length > 0) {
                setSelectedConnection(data[0].id);
            }
        } catch (error) {
            console.error("Error fetching connections:", error);
        }
    };

    const handleSend = async () => {
        if (!input.trim() || !selectedConnection) return;

        const userMessage: Message = {
            role: "user",
            content: input
        };

        setMessages([...messages, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const data = await apiClient.post("/api/v1/agent/chat", {
                query: input,
                connection_id: selectedConnection,
                session_id: sessionId,
                execute_sql: true
            });

            // Update session ID
            if (!sessionId && data.session_id) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                role: "assistant",
                content: data.explanation || "Query executed successfully",
                sql: data.sql,
                explanation: data.explanation,
                execution: data.execution
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error: any) {
            const errorMessage: Message = {
                role: "assistant",
                content: `Error: ${error.message || "Failed to process query"}`
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="h-screen flex flex-col">
            {/* Header */}
            <div className="border-b px-6 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">AI Data Analyst</h1>
                        <p className="text-sm text-muted-foreground">Ask questions about your data in natural language</p>
                    </div>
                    <div className="w-64">
                        <Select
                            value={selectedConnection?.toString()}
                            onValueChange={(value) => setSelectedConnection(parseInt(value))}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Select connection" />
                            </SelectTrigger>
                            <SelectContent>
                                {connections.map((conn) => (
                                    <SelectItem key={conn.id} value={conn.id.toString()}>
                                        <div className="flex items-center gap-2">
                                            <Database className="h-4 w-4" />
                                            {conn.name}
                                        </div>
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="text-center max-w-md">
                            <Database className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                            <h2 className="text-xl font-semibold mb-2">Start a conversation</h2>
                            <p className="text-muted-foreground mb-4">
                                Ask questions about your data and I'll generate SQL queries to answer them.
                            </p>
                            <div className="text-left space-y-2 text-sm text-muted-foreground">
                                <p>Try asking:</p>
                                <ul className="list-disc list-inside space-y-1">
                                    <li>"Show me the top 10 customers by revenue"</li>
                                    <li>"What's the average order value this month?"</li>
                                    <li>"List all products with low stock"</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                            >
                                <div className={`max-w-3xl ${message.role === "user" ? "w-auto" : "w-full"}`}>
                                    {message.role === "user" ? (
                                        <div className="bg-primary text-primary-foreground rounded-lg px-4 py-2">
                                            {message.content}
                                        </div>
                                    ) : (
                                        <Card>
                                            <CardContent className="pt-6 space-y-4">
                                                {/* Explanation */}
                                                {message.explanation && (
                                                    <p className="text-sm">{message.explanation}</p>
                                                )}

                                                {/* SQL Query */}
                                                {message.sql && (
                                                    <div>
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <Code className="h-4 w-4" />
                                                            <span className="text-sm font-medium">Generated SQL</span>
                                                        </div>
                                                        <pre className="bg-muted p-3 rounded-lg overflow-x-auto text-xs">
                                                            <code>{message.sql}</code>
                                                        </pre>
                                                    </div>
                                                )}

                                                {/* Execution Results */}
                                                {message.execution && (
                                                    <div>
                                                        <div className="flex items-center gap-2 mb-2">
                                                            {message.execution.success ? (
                                                                <CheckCircle className="h-4 w-4 text-green-600" />
                                                            ) : (
                                                                <XCircle className="h-4 w-4 text-red-600" />
                                                            )}
                                                            <span className="text-sm font-medium">
                                                                {message.execution.success
                                                                    ? `Results (${message.execution.row_count} rows)`
                                                                    : "Execution Error"}
                                                            </span>
                                                        </div>

                                                        {message.execution.success ? (
                                                            <div className="border rounded-lg overflow-hidden">
                                                                <div className="overflow-x-auto">
                                                                    <table className="w-full text-sm">
                                                                        <thead className="bg-muted">
                                                                            <tr>
                                                                                {message.execution.columns.map((col) => (
                                                                                    <th key={col} className="text-left p-2 font-medium">
                                                                                        {col}
                                                                                    </th>
                                                                                ))}
                                                                            </tr>
                                                                        </thead>
                                                                        <tbody>
                                                                            {message.execution.rows.slice(0, 10).map((row, i) => (
                                                                                <tr key={i} className="border-t">
                                                                                    {message.execution!.columns.map((col) => (
                                                                                        <td key={col} className="p-2">
                                                                                            {row[col]?.toString() || "-"}
                                                                                        </td>
                                                                                    ))}
                                                                                </tr>
                                                                            ))}
                                                                        </tbody>
                                                                    </table>
                                                                </div>
                                                                {message.execution.row_count > 10 && (
                                                                    <div className="bg-muted px-2 py-1 text-xs text-muted-foreground text-center">
                                                                        Showing 10 of {message.execution.row_count} rows
                                                                    </div>
                                                                )}
                                                            </div>
                                                        ) : (
                                                            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-800">
                                                                {message.execution.error}
                                                            </div>
                                                        )}
                                                    </div>
                                                )}

                                                {/* Plain content if no structured data */}
                                                {!message.sql && !message.execution && (
                                                    <p className="text-sm">{message.content}</p>
                                                )}
                                            </CardContent>
                                        </Card>
                                    )}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            {/* Input */}
            <div className="border-t p-4">
                <div className="max-w-4xl mx-auto flex gap-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask a question about your data..."
                        disabled={loading || !selectedConnection}
                        className="flex-1"
                    />
                    <Button
                        onClick={handleSend}
                        disabled={loading || !input.trim() || !selectedConnection}
                    >
                        {loading ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                            <Send className="h-4 w-4" />
                        )}
                    </Button>
                </div>
                {!selectedConnection && (
                    <p className="text-xs text-center text-muted-foreground mt-2">
                        Please select a database connection to start chatting
                    </p>
                )}
            </div>
        </div>
    );
}
