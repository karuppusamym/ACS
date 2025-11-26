"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Database, Plus, Table } from "lucide-react";

interface Connection {
    id: number;
    name: string;
    type: string;
    connection_string?: string;
    is_active: boolean;
}

export default function ModelsPage() {
    const router = useRouter();
    const [connections, setConnections] = useState<Connection[]>([]);
    const [loading, setLoading] = useState(true);

    // Fetch connections from API on mount
    useEffect(() => {
        const fetchConnections = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/v1/connection/connections');
                if (response.ok) {
                    const data = await response.json();
                    setConnections(data);
                } else {
                    console.error('Failed to fetch connections:', response.status);
                }
            } catch (error) {
                console.error('Error fetching connections:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchConnections();
    }, []);
    const [showNewConnection, setShowNewConnection] = useState(false);
    const [newConnection, setNewConnection] = useState({
        name: "",
        type: "postgresql",
        host: "",
        port: "5432",
        database: "",
        username: "",
        password: "",
    });

    const handleAddConnection = async () => {
        try {
            // Call the backend API to save the connection
            const response = await fetch('http://127.0.0.1:8000/api/v1/connection/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: newConnection.name,
                    type: newConnection.type,
                    host: newConnection.host,
                    port: parseInt(newConnection.port),
                    database: newConnection.database,
                    username: newConnection.username,
                    password: newConnection.password,
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                console.error('Failed to save connection:', error);
                alert(`Failed to save connection: ${error.error?.message || 'Unknown error'}`);
                return;
            }

            const savedConnection = await response.json();
            console.log('Connection saved successfully:', savedConnection);

            // Add to local state for UI update
            const connection: Connection = {
                id: savedConnection.id || Date.now().toString(),
                name: newConnection.name,
                type: newConnection.type,
                status: "connected",
            };
            setConnections([...connections, connection]);
            setShowNewConnection(false);
            setNewConnection({
                name: "",
                type: "postgresql",
                host: "",
                port: "5432",
                database: "",
                username: "",
                password: "",
            });
        } catch (error) {
            console.error('Error saving connection:', error);
            alert('Failed to save connection. Please check the console for details.');
        }
    };

    return (
        <div className="h-full flex flex-col">
            <div className="flex items-center justify-between border-b px-6 py-4">
                <h1 className="text-2xl font-bold">Data Models</h1>
                <Button onClick={() => setShowNewConnection(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    New Connection
                </Button>
            </div>
            <div className="flex-1 overflow-auto p-6">
                <div className="max-w-4xl space-y-6">
                    {/* Existing Connections */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Database Connections</CardTitle>
                            <CardDescription>
                                Manage your database connections and define semantic models.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {connections.map((conn) => (
                                    <div
                                        key={conn.id}
                                        className="flex items-center gap-4 rounded-lg border p-4 hover:bg-muted/50 transition-colors"
                                    >
                                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                                            <Database className="h-5 w-5 text-primary" />
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2">
                                                <h3 className="font-medium">{conn.name}</h3>
                                                <span
                                                    className={`rounded-full px-2 py-0.5 text-xs ${conn.is_active
                                                        ? "bg-green-100 text-green-700"
                                                        : "bg-gray-100 text-gray-700"
                                                        }`}
                                                >
                                                    {conn.is_active ? "active" : "inactive"}
                                                </span>
                                            </div>
                                            <p className="text-sm text-muted-foreground">{conn.type}</p>
                                        </div>
                                        <div className="flex gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => router.push(`/tables/${encodeURIComponent(conn.name)}`)}
                                            >
                                                <Table className="mr-2 h-4 w-4" />
                                                View Tables
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => router.push(`/semantic/${encodeURIComponent(conn.name)}`)}
                                            >
                                                Configure
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* New Connection Form */}
                    {showNewConnection && (
                        <Card>
                            <CardHeader>
                                <CardTitle>New Database Connection</CardTitle>
                                <CardDescription>
                                    Connect to your database to start analyzing data.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid gap-4 md:grid-cols-2">
                                    <div className="grid gap-2">
                                        <Label htmlFor="conn-name">Connection Name</Label>
                                        <Input
                                            id="conn-name"
                                            placeholder="My Database"
                                            value={newConnection.name}
                                            onChange={(e) => setNewConnection({ ...newConnection, name: e.target.value })}
                                        />
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="conn-type">Database Type</Label>
                                        <Select
                                            value={newConnection.type}
                                            onValueChange={(value) => setNewConnection({ ...newConnection, type: value })}
                                        >
                                            <SelectTrigger id="conn-type">
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="postgresql">PostgreSQL</SelectItem>
                                                <SelectItem value="mysql">MySQL</SelectItem>
                                                <SelectItem value="mssql">Microsoft SQL Server</SelectItem>
                                                <SelectItem value="oracle">Oracle</SelectItem>
                                                <SelectItem value="snowflake">Snowflake</SelectItem>
                                                <SelectItem value="bigquery">Google BigQuery</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>
                                <div className="grid gap-4 md:grid-cols-2">
                                    <div className="grid gap-2">
                                        <Label htmlFor="host">Host</Label>
                                        <Input
                                            id="host"
                                            placeholder="localhost"
                                            value={newConnection.host}
                                            onChange={(e) => setNewConnection({ ...newConnection, host: e.target.value })}
                                        />
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="port">Port</Label>
                                        <Input
                                            id="port"
                                            placeholder="5432"
                                            value={newConnection.port}
                                            onChange={(e) => setNewConnection({ ...newConnection, port: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="database">Database Name</Label>
                                    <Input
                                        id="database"
                                        placeholder="my_database"
                                        value={newConnection.database}
                                        onChange={(e) => setNewConnection({ ...newConnection, database: e.target.value })}
                                    />
                                </div>
                                <div className="grid gap-4 md:grid-cols-2">
                                    <div className="grid gap-2">
                                        <Label htmlFor="username">Username</Label>
                                        <Input
                                            id="username"
                                            placeholder="postgres"
                                            value={newConnection.username}
                                            onChange={(e) => setNewConnection({ ...newConnection, username: e.target.value })}
                                        />
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="password">Password</Label>
                                        <Input
                                            id="password"
                                            type="password"
                                            value={newConnection.password}
                                            onChange={(e) => setNewConnection({ ...newConnection, password: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <Button onClick={handleAddConnection}>Connect</Button>
                                    <Button variant="outline" onClick={() => setShowNewConnection(false)}>
                                        Cancel
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Semantic Models Info */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Semantic Layer</CardTitle>
                            <CardDescription>
                                Add business descriptions and define relationships for your tables.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="rounded-lg border border-dashed p-8 text-center">
                                <Table className="mx-auto h-12 w-12 text-muted-foreground" />
                                <h3 className="mt-4 font-medium">No semantic models yet</h3>
                                <p className="mt-2 text-sm text-muted-foreground">
                                    Connect a database and click "View Tables" to start adding business context
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div >
    );
}
