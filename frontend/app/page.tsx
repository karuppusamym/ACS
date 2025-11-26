"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Database, MessageSquare, Activity, TrendingUp } from "lucide-react";
import Link from "next/link";
import axios from "axios";
import { useGlobalError } from "@/components/global-error-provider";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function HomePage() {
  const { showError } = useGlobalError();

  // Fetch recent models
  const { data: models = [] } = useQuery({
    queryKey: ["models"],
    queryFn: async () => {
      try {
        const response = await axios.get(`${API_URL}/api/v1/models`);
        return response.data;
      } catch (error) {
        showError("Failed to load models. Is the backend running?");
        return [];
      }
    },
  });

  // Fetch recent sessions
  const { data: sessions = [] } = useQuery({
    queryKey: ["sessions"],
    queryFn: async () => {
      try {
        const response = await axios.get(`${API_URL}/api/v1/chat/sessions`);
        return response.data;
      } catch (error) {
        // Don't show duplicate errors if both fail
        return [];
      }
    },
  });

  const stats = [
    {
      title: "Total Models",
      value: models.length,
      icon: Database,
      color: "text-blue-600",
      bgColor: "bg-blue-100",
    },
    {
      title: "Chat Sessions",
      value: sessions.length,
      icon: MessageSquare,
      color: "text-green-600",
      bgColor: "bg-green-100",
    },
    {
      title: "Queries Today",
      value: "0",
      icon: Activity,
      color: "text-purple-600",
      bgColor: "bg-purple-100",
    },
    {
      title: "Insights Generated",
      value: "0",
      icon: TrendingUp,
      color: "text-orange-600",
      bgColor: "bg-orange-100",
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Welcome to Agentic Data Analyst</h1>
          <p className="text-gray-500 mt-1">AI-powered insights for your data</p>
        </div>
        <div className="flex gap-2">
          <Link href="/models">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Model
            </Button>
          </Link>
          <Link href="/analysis">
            <Button variant="outline">
              <MessageSquare className="mr-2 h-4 w-4" />
              New Chat
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Models and Sessions */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Models */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Models</CardTitle>
            <CardDescription>Your data models and connections</CardDescription>
          </CardHeader>
          <CardContent>
            {models.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Database className="mx-auto h-12 w-12 mb-2 opacity-50" />
                <p>No models yet</p>
                <Link href="/models">
                  <Button variant="link" className="mt-2">
                    Create your first model
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {models.slice(0, 5).map((model: any) => (
                  <Link key={model.id} href={`/models/${model.id}`}>
                    <div className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-100">
                          <Database className="h-4 w-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium">{model.name}</p>
                          <p className="text-sm text-gray-500">{model.type}</p>
                        </div>
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded-full ${model.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-700"
                          }`}
                      >
                        {model.is_active ? "Active" : "Inactive"}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Sessions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Chats</CardTitle>
            <CardDescription>Your analysis sessions</CardDescription>
          </CardHeader>
          <CardContent>
            {sessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <MessageSquare className="mx-auto h-12 w-12 mb-2 opacity-50" />
                <p>No chat sessions yet</p>
                <Link href="/analysis">
                  <Button variant="link" className="mt-2">
                    Start your first analysis
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {sessions.slice(0, 5).map((session: any) => (
                  <Link key={session.id} href={`/analysis?session=${session.id}`}>
                    <div className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-green-100">
                          <MessageSquare className="h-4 w-4 text-green-600" />
                        </div>
                        <div>
                          <p className="font-medium">{session.name || "Untitled Chat"}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(session.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Get started with common tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Link href="/models">
              <div className="p-4 rounded-lg border hover:border-primary transition-colors cursor-pointer">
                <Database className="h-8 w-8 text-blue-600 mb-2" />
                <h3 className="font-medium mb-1">Connect Database</h3>
                <p className="text-sm text-gray-500">
                  Add a new data source and sync schema
                </p>
              </div>
            </Link>
            <Link href="/analysis">
              <div className="p-4 rounded-lg border hover:border-primary transition-colors cursor-pointer">
                <MessageSquare className="h-8 w-8 text-green-600 mb-2" />
                <h3 className="font-medium mb-1">Ask Questions</h3>
                <p className="text-sm text-gray-500">
                  Use AI to analyze your data with natural language
                </p>
              </div>
            </Link>
            <Link href="/process-mining">
              <div className="p-4 rounded-lg border hover:border-primary transition-colors cursor-pointer">
                <Activity className="h-8 w-8 text-purple-600 mb-2" />
                <h3 className="font-medium mb-1">Process Mining</h3>
                <p className="text-sm text-gray-500">
                  Discover and optimize business processes
                </p>
              </div>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
