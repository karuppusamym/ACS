"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Database, Key, Link, Index, CheckCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface Column {
    name: string;
    type: string;
    nullable: boolean;
    default: string | null;
    autoincrement: boolean;
}

interface ForeignKey {
    name: string | null;
    columns: string[];
    referred_table: string;
    referred_columns: string[];
}

interface IndexInfo {
    name: string | null;
    columns: string[];
    unique: boolean;
}

interface TableMetadata {
    name: string;
    columns: Column[];
    primary_key: string[];
    foreign_keys: ForeignKey[];
    indexes: IndexInfo[];
    unique_constraints: any[];
    check_constraints: any[];
    row_count: number | null;
}

export default function TablesPage() {
    const params = useParams();
    const router = useRouter();
    const connectionName = params.connection as string;

    const [tables, setTables] = useState<TableMetadata[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);

    useEffect(() => {
        const fetchTables = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/api/v1/connection/metadata/${connectionName}`);
                if (response.ok) {
                    const data = await response.json();
                    setTables(data);
                    if (data.length > 0) {
                        setSelectedTable(data[0].name);
                    }
                } else {
                    console.error('Failed to fetch tables:', response.status);
                }
            } catch (error) {
                console.error('Error fetching tables:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchTables();
    }, [connectionName]);

    const selectedTableData = tables.find(t => t.name === selectedTable);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <Database className="h-12 w-12 mx-auto mb-4 animate-pulse text-primary" />
                    <p className="text-muted-foreground">Loading tables...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-screen flex flex-col">
            <div className="border-b px-6 py-4 flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back
                </Button>
                <div>
                    <h1 className="text-2xl font-bold">{connectionName}</h1>
                    <p className="text-sm text-muted-foreground">{tables.length} tables</p>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Table List Sidebar */}
                <div className="w-64 border-r overflow-y-auto p-4">
                    <h2 className="font-semibold mb-3">Tables</h2>
                    <div className="space-y-1">
                        {tables.map((table) => (
                            <button
                                key={table.name}
                                onClick={() => setSelectedTable(table.name)}
                                className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${selectedTable === table.name
                                    ? "bg-primary text-primary-foreground"
                                    : "hover:bg-muted"
                                    }`}
                            >
                                <div className="flex items-center gap-2">
                                    <Database className="h-4 w-4" />
                                    <span className="truncate">{table.name}</span>
                                </div>
                                {table.row_count !== null && (
                                    <div className="text-xs opacity-70 mt-1">
                                        {table.row_count.toLocaleString()} rows
                                    </div>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Table Details */}
                <div className="flex-1 overflow-y-auto p-6">
                    {selectedTableData ? (
                        <div className="max-w-5xl space-y-6">
                            {/* Columns */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Columns</CardTitle>
                                    <CardDescription>
                                        {selectedTableData.columns.length} columns in {selectedTableData.name}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="border rounded-lg overflow-hidden">
                                        <table className="w-full">
                                            <thead className="bg-muted">
                                                <tr>
                                                    <th className="text-left p-3 font-medium">Name</th>
                                                    <th className="text-left p-3 font-medium">Type</th>
                                                    <th className="text-left p-3 font-medium">Constraints</th>
                                                    <th className="text-left p-3 font-medium">Default</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {selectedTableData.columns.map((col, idx) => (
                                                    <tr key={idx} className="border-t">
                                                        <td className="p-3">
                                                            <div className="flex items-center gap-2">
                                                                {selectedTableData.primary_key.includes(col.name) && (
                                                                    <Key className="h-4 w-4 text-yellow-600" />
                                                                )}
                                                                <span className="font-mono text-sm">{col.name}</span>
                                                            </div>
                                                        </td>
                                                        <td className="p-3">
                                                            <Badge variant="outline">{col.type}</Badge>
                                                        </td>
                                                        <td className="p-3">
                                                            <div className="flex gap-1">
                                                                {!col.nullable && (
                                                                    <Badge variant="secondary" className="text-xs">NOT NULL</Badge>
                                                                )}
                                                                {col.autoincrement && (
                                                                    <Badge variant="secondary" className="text-xs">AUTO</Badge>
                                                                )}
                                                            </div>
                                                        </td>
                                                        <td className="p-3 text-sm text-muted-foreground">
                                                            {col.default || "-"}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Foreign Keys */}
                            {selectedTableData.foreign_keys.length > 0 && (
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <Link className="h-5 w-5" />
                                            Foreign Keys
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-3">
                                            {selectedTableData.foreign_keys.map((fk, idx) => (
                                                <div key={idx} className="p-3 border rounded-lg">
                                                    <div className="font-mono text-sm">
                                                        {fk.columns.join(", ")} → {fk.referred_table}({fk.referred_columns.join(", ")})
                                                    </div>
                                                    {fk.name && (
                                                        <div className="text-xs text-muted-foreground mt-1">{fk.name}</div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            )}

                            {/* Indexes */}
                            {selectedTableData.indexes.length > 0 && (
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <Index className="h-5 w-5" />
                                            Indexes
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-2">
                                            {selectedTableData.indexes.map((idx, i) => (
                                                <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
                                                    <div>
                                                        <div className="font-mono text-sm">{idx.columns.join(", ")}</div>
                                                        {idx.name && (
                                                            <div className="text-xs text-muted-foreground">{idx.name}</div>
                                                        )}
                                                    </div>
                                                    {idx.unique && (
                                                        <Badge variant="secondary">UNIQUE</Badge>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            )}
                        </div>
                    ) : (
                        <div className="flex items-center justify-center h-full">
                            <p className="text-muted-foreground">Select a table to view details</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
