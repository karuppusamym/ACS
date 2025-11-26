"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DataChart } from "@/components/charts/data-chart";
import { Send, Loader2, Code, BarChart3, Table as TableIcon } from "lucide-react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message {
    id: number;
    role: string;
    content: string;
    metadata?: {
        sql?: string;
        chart_config?: any;
        trace?: any[];
    };
    created_at: string;
}

interface ChatResponse {
    message: Message;
    sql?: string;
    chart_config?: any;
    data?: any[];
    trace?: any[];
}

export function EnhancedChatInterface({ sessionId }: { sessionId: number }) {
    const [input, setInput] = useState("");
    const queryClient = useQueryClient();

    // Fetch messages
    const { data: messages = [], isLoading } = useQuery({
        queryKey: ["messages", sessionId],
        queryFn: async () => {
            const response = await axios.get(`${API_URL}/api/v1/chat/sessions/${sessionId}/messages`);
            return response.data;
        },
        refetchInterval: 5000, // Refresh every 5 seconds
    });

    // Send message mutation
    const sendMessage = useMutation({
        mutationFn: async (content: string) => {
            const response = await axios.post<ChatResponse>(
                `${API_URL}/api/v1/chat/sessions/${sessionId}/messages`,
                { role: "user", content }
            );
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["messages", sessionId] });
            setInput("");
        },
    });

    const handleSend = () => {
        if (!input.trim() || sendMessage.isPending) return;
        sendMessage.mutate(input);
    };

    const lastAssistantMessage = messages
        .filter((m: Message) => m.role === "assistant")
        .slice(-1)[0];

    return (
        <div className="flex h-full gap-4">
            {/* Chat Messages */}
            <div className="flex-1 flex flex-col">
                <Card className="flex-1 flex flex-col">
                    <CardHeader>
                        <CardTitle>Conversation</CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-auto space-y-4">
                        {isLoading ? (
                            <div className="flex items-center justify-center h-full">
                                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            </div>
                        ) : messages.length === 0 ? (
                            <div className="flex items-center justify-center h-full text-gray-500">
                                <p>Start a conversation by asking a question about your data</p>
                            </div>
                        ) : (
                            messages.map((message: Message) => (
                                <div
                                    key={message.id}
                                    className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                                >
                                    <div
                                        className={`max-w-[80%] rounded-lg px-4 py-2 ${message.role === "user"
                                                ? "bg-primary text-primary-foreground"
                                                : "bg-muted"
                                            }`}
                                    >
                                        <p className="text-sm">{message.content}</p>
                                        {message.metadata?.trace && (
                                            <p className="text-xs opacity-70 mt-1">
                                                {message.metadata.trace.length} steps
                                            </p>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                        {sendMessage.isPending && (
                            <div className="flex justify-start">
                                <div className="bg-muted rounded-lg px-4 py-2">
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                </div>
                            </div>
                        )}
                    </CardContent>
                    <div className="p-4 border-t">
                        <div className="flex gap-2">
                            <Input
                                placeholder="Ask a question about your data..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                                disabled={sendMessage.isPending}
                            />
                            <Button onClick={handleSend} disabled={sendMessage.isPending || !input.trim()}>
                                {sendMessage.isPending ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Send className="h-4 w-4" />
                                )}
                            </Button>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Results Panel */}
            <div className="w-1/2">
                <Card className="h-full">
                    <CardHeader>
                        <CardTitle>Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {lastAssistantMessage?.metadata ? (
                            <Tabs defaultValue="chart" className="w-full">
                                <TabsList className="grid w-full grid-cols-3">
                                    <TabsTrigger value="chart">
                                        <BarChart3 className="h-4 w-4 mr-2" />
                                        Chart
                                    </TabsTrigger>
                                    <TabsTrigger value="data">
                                        <TableIcon className="h-4 w-4 mr-2" />
                                        Data
                                    </TabsTrigger>
                                    <TabsTrigger value="sql">
                                        <Code className="h-4 w-4 mr-2" />
                                        SQL
                                    </TabsTrigger>
                                </TabsList>
                                <TabsContent value="chart" className="mt-4">
                                    {sendMessage.data?.data && sendMessage.data?.chart_config ? (
                                        <DataChart
                                            data={sendMessage.data.data}
                                            config={sendMessage.data.chart_config}
                                        />
                                    ) : (
                                        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
                                            <p className="text-gray-500">No chart data available</p>
                                        </div>
                                    )}
                                </TabsContent>
                                <TabsContent value="data" className="mt-4">
                                    {sendMessage.data?.data ? (
                                        <DataChart
                                            data={sendMessage.data.data}
                                            config={{ type: "table" }}
                                        />
                                    ) : (
                                        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
                                            <p className="text-gray-500">No data available</p>
                                        </div>
                                    )}
                                </TabsContent>
                                <TabsContent value="sql" className="mt-4">
                                    {lastAssistantMessage.metadata.sql ? (
                                        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-auto max-h-96">
                                            <code>{lastAssistantMessage.metadata.sql}</code>
                                        </pre>
                                    ) : (
                                        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
                                            <p className="text-gray-500">No SQL available</p>
                                        </div>
                                    )}
                                </TabsContent>
                            </Tabs>
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-500">
                                <p>Results will appear here after you ask a question</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
