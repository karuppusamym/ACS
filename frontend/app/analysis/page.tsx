"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { EnhancedChatInterface } from "@/components/chat/enhanced-chat-interface";
import { Plus, Loader2 } from "lucide-react";
import apiClient from "@/lib/api-client";

export default function AnalysisPage() {
    const [selectedModel, setSelectedModel] = useState<string>("");
    const [selectedSession, setSelectedSession] = useState<number | null>(null);

    // Fetch models
    const { data: models = [], isLoading: modelsLoading } = useQuery({
        queryKey: ["models"],
        queryFn: async () => {
            return await apiClient.get("/api/v1/models");
        },
    });

    // Fetch sessions
    const { data: sessions = [], refetch: refetchSessions } = useQuery({
        queryKey: ["sessions"],
        queryFn: async () => {
            return await apiClient.sessions.list();
        },
    });

    const handleCreateSession = async () => {
        if (!selectedModel) return;

        try {
            const response = await apiClient.sessions.create({
                name: `Analysis ${new Date().toLocaleString()}`,
                connection_id: parseInt(selectedModel),
            });

            setSelectedSession(response.id);
            refetchSessions();
        } catch (error) {
            console.error("Failed to create session:", error);
        }
    };

    return (
        <div className="h-full p-6">
            {!selectedSession ? (
                <div className="max-w-2xl mx-auto mt-20">
                    <Card>
                        <CardHeader>
                            <CardTitle>Start a New Analysis</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <label className="text-sm font-medium mb-2 block">Select a Model</label>
                                {modelsLoading ? (
                                    <div className="flex items-center justify-center py-8">
                                        <Loader2 className="h-6 w-6 animate-spin" />
                                    </div>
                                ) : models.length === 0 ? (
                                    <div className="text-center py-8 text-gray-500">
                                        <p>No models available. Create a model first.</p>
                                    </div>
                                ) : (
                                    <Select value={selectedModel} onValueChange={setSelectedModel}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Choose a data model" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {models.map((model: any) => (
                                                <SelectItem key={model.id} value={model.id.toString()}>
                                                    {model.name} ({model.type})
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                )}
                            </div>

                            <Button
                                onClick={handleCreateSession}
                                disabled={!selectedModel}
                                className="w-full"
                            >
                                <Plus className="mr-2 h-4 w-4" />
                                Create New Chat Session
                            </Button>

                            {sessions.length > 0 && (
                                <div className="mt-6">
                                    <h3 className="text-sm font-medium mb-2">Or continue a previous session</h3>
                                    <div className="space-y-2">
                                        {sessions.slice(0, 5).map((session: any) => (
                                            <Button
                                                key={session.id}
                                                variant="outline"
                                                className="w-full justify-start"
                                                onClick={() => setSelectedSession(session.id)}
                                            >
                                                {session.name || "Untitled Chat"}
                                            </Button>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            ) : (
                <div className="h-full flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                        <h1 className="text-2xl font-bold">Analysis Session</h1>
                        <Button variant="outline" onClick={() => setSelectedSession(null)}>
                            Back to Sessions
                        </Button>
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <EnhancedChatInterface sessionId={selectedSession} />
                    </div>
                </div>
            )}
        </div>
    );
}
