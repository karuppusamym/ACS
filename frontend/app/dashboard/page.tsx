"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart3, LineChart, PieChart, TrendingUp, Database, Activity } from "lucide-react";

interface Connection {
    id: number;
    name: string;
    type: string;
}

interface DashboardStat {
    title: string;
    value: string | number;
    change?: string;
    icon: any;
    color: string;
}

export default function DashboardPage() {
    const [connections, setConnections] = useState<Connection[]>([]);
    const [selectedConnection, setSelectedConnection] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchConnections();
    }, []);

    const fetchConnections = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/v1/connection/connections");
            if (response.ok) {
                const data = await response.json();
                setConnections(data);
                if (data.length > 0) {
                    setSelectedConnection(data[0].id);
                }
            }
        } catch (error) {
            console.error("Error fetching connections:", error);
        } finally {
            setLoading(false);
        }
    };

    const stats: DashboardStat[] = [
        {
            title: "Total Queries",
            value: "1,234",
            change: "+12%",
            icon: Activity,
            color: "text-blue-600"
        },
        {
            title: "Active Connections",
            value: connections.length,
            icon: Database,
            color: "text-green-600"
        },
        {
            title: "Semantic Models",
            value: "8",
            change: "+3",
            icon: BarChart3,
            color: "text-purple-600"
        },
        {
            title: "Insights Generated",
            value: "42",
            change: "+18%",
            icon: TrendingUp,
            color: "text-orange-600"
        }
    ];

    return (
        <div className="h-screen flex flex-col">
            {/* Header */}
            <div className="border-b px-6 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Dashboard</h1>
                        <p className="text-sm text-muted-foreground">Overview of your data analytics</p>
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
                                        {conn.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Stats Grid */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    {stats.map((stat) => (
                        <Card key={stat.title}>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                                <stat.icon className={`h-4 w-4 ${stat.color}`} />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stat.value}</div>
                                {stat.change && (
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {stat.change} from last month
                                    </p>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>

                {/* Charts */}
                <div className="grid gap-6 md:grid-cols-2">
                    {/* Query Trends */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Query Trends</CardTitle>
                            <CardDescription>Daily query volume over the last 7 days</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="h-64 flex items-center justify-center border rounded-lg bg-muted/20">
                                <div className="text-center text-muted-foreground">
                                    <LineChart className="h-12 w-12 mx-auto mb-2 opacity-50" />
                                    <p className="text-sm">Chart visualization coming soon</p>
                                    <p className="text-xs">Integrate with Chart.js or Recharts</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Table Usage */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Table Usage</CardTitle>
                            <CardDescription>Most queried tables this week</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="h-64 flex items-center justify-center border rounded-lg bg-muted/20">
                                <div className="text-center text-muted-foreground">
                                    <PieChart className="h-12 w-12 mx-auto mb-2 opacity-50" />
                                    <p className="text-sm">Chart visualization coming soon</p>
                                    <p className="text-xs">Integrate with Chart.js or Recharts</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Recent Activity */}
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Activity</CardTitle>
                        <CardDescription>Latest queries and insights</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="flex items-start gap-4 pb-4 border-b last:border-0">
                                    <div className="p-2 bg-primary/10 rounded-lg">
                                        <Activity className="h-4 w-4 text-primary" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium">Query executed successfully</p>
                                        <p className="text-xs text-muted-foreground">
                                            SELECT * FROM customers WHERE status = 'active'
                                        </p>
                                        <p className="text-xs text-muted-foreground mt-1">
                                            {i} hour{i > 1 ? 's' : ''} ago
                                        </p>
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        {Math.floor(Math.random() * 100)} rows
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card>
                    <CardHeader>
                        <CardTitle>Quick Actions</CardTitle>
                        <CardDescription>Common tasks and shortcuts</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid gap-3 md:grid-cols-3">
                            <Button variant="outline" className="justify-start">
                                <Database className="mr-2 h-4 w-4" />
                                New Connection
                            </Button>
                            <Button variant="outline" className="justify-start">
                                <BarChart3 className="mr-2 h-4 w-4" />
                                Create Model
                            </Button>
                            <Button variant="outline" className="justify-start">
                                <Activity className="mr-2 h-4 w-4" />
                                Start Chat
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
