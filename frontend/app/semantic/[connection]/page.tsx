"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Sparkles, Save, RefreshCw } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

interface SemanticModel {
    id: number;
    table_name: string;
    connection_id: number;
    business_description: string | null;
    column_descriptions: Record<string, string> | null;
    system_prompt: string | null;
    user_prompt_template: string | null;
    business_glossary: Record<string, string> | null;
    example_queries: string[] | null;
    auto_generated_context: any | null;
    prompt_version: number;
}

interface TableMetadata {
    name: string;
    columns: Array<{
        name: string;
        type: string;
        nullable: boolean;
    }>;
}

export default function SemanticEditorPage() {
    const params = useParams();
    const router = useRouter();
    const connectionId = params.connection as string;

    const [tables, setTables] = useState<TableMetadata[]>([]);
    const [models, setModels] = useState<SemanticModel[]>([]);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [currentModel, setCurrentModel] = useState<SemanticModel | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [generating, setGenerating] = useState(false);

    // Form state
    const [businessDescription, setBusinessDescription] = useState("");
    const [columnDescriptions, setColumnDescriptions] = useState<Record<string, string>>({});
    const [systemPrompt, setSystemPrompt] = useState("");
    const [businessGlossary, setBusinessGlossary] = useState<Record<string, string>>({});
    const [newGlossaryTerm, setNewGlossaryTerm] = useState("");
    const [newGlossaryDef, setNewGlossaryDef] = useState("");

    useEffect(() => {
        fetchData();
    }, [connectionId]);

    useEffect(() => {
        if (currentModel) {
            setBusinessDescription(currentModel.business_description || "");
            setColumnDescriptions(currentModel.column_descriptions || {});
            setSystemPrompt(currentModel.system_prompt || "");
            setBusinessGlossary(currentModel.business_glossary || {});
        }
    }, [currentModel]);

    const fetchData = async () => {
        try {
            // Fetch tables metadata
            const tablesRes = await fetch(`http://127.0.0.1:8000/api/v1/connection/metadata/${connectionId}`);
            if (tablesRes.ok) {
                const tablesData = await tablesRes.json();
                setTables(tablesData);
                if (tablesData.length > 0) {
                    setSelectedTable(tablesData[0].name);
                }
            }

            // Fetch semantic models
            const modelsRes = await fetch(`http://127.0.0.1:8000/api/v1/semantic/models/${connectionId}`);
            if (modelsRes.ok) {
                const modelsData = await modelsRes.json();
                setModels(modelsData);
            }
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (selectedTable) {
            const model = models.find(m => m.table_name === selectedTable);
            setCurrentModel(model || null);
        }
    }, [selectedTable, models]);

    const handleGenerateContext = async () => {
        if (!selectedTable) return;

        setGenerating(true);
        try {
            // Create model if it doesn't exist
            let modelId = currentModel?.id;
            if (!currentModel) {
                const createRes = await fetch(`http://127.0.0.1:8000/api/v1/semantic/model`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        table_name: selectedTable,
                        connection_id: parseInt(connectionId)
                    })
                });
                if (createRes.ok) {
                    const newModel = await createRes.json();
                    modelId = newModel.id;
                    setModels([...models, newModel]);
                }
            }

            // Generate context
            const res = await fetch(`http://127.0.0.1:8000/api/v1/semantic/model/${modelId}/generate-context`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ table_name: selectedTable })
            });

            if (res.ok) {
                const data = await res.json();
                const context = data.context;

                // Update form with generated context
                if (context.business_description) {
                    setBusinessDescription(context.business_description);
                }
                if (context.column_descriptions) {
                    setColumnDescriptions(context.column_descriptions);
                }
                if (context.business_glossary) {
                    setBusinessGlossary(context.business_glossary);
                }

                // Refresh models
                await fetchData();
            }
        } catch (error) {
            console.error("Error generating context:", error);
        } finally {
            setGenerating(false);
        }
    };

    const handleSave = async () => {
        if (!selectedTable) return;

        setSaving(true);
        try {
            const payload = {
                business_description: businessDescription,
                column_descriptions: columnDescriptions,
                system_prompt: systemPrompt,
                business_glossary: businessGlossary
            };

            if (currentModel) {
                // Update existing model
                await fetch(`http://127.0.0.1:8000/api/v1/semantic/model/${currentModel.id}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
            } else {
                // Create new model
                await fetch(`http://127.0.0.1:8000/api/v1/semantic/model`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        table_name: selectedTable,
                        connection_id: parseInt(connectionId),
                        ...payload
                    })
                });
            }

            await fetchData();
        } catch (error) {
            console.error("Error saving model:", error);
        } finally {
            setSaving(false);
        }
    };

    const handleAddGlossaryTerm = () => {
        if (newGlossaryTerm && newGlossaryDef) {
            setBusinessGlossary({
                ...businessGlossary,
                [newGlossaryTerm]: newGlossaryDef
            });
            setNewGlossaryTerm("");
            setNewGlossaryDef("");
        }
    };

    const selectedTableData = tables.find(t => t.name === selectedTable);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <RefreshCw className="h-12 w-12 mx-auto mb-4 animate-spin text-primary" />
                    <p className="text-muted-foreground">Loading semantic models...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-screen flex flex-col">
            <div className="border-b px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="sm" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back
                    </Button>
                    <div>
                        <h1 className="text-2xl font-bold">Semantic Layer Editor</h1>
                        <p className="text-sm text-muted-foreground">Add business context to your data</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button onClick={handleGenerateContext} disabled={generating || !selectedTable}>
                        <Sparkles className="h-4 w-4 mr-2" />
                        {generating ? "Generating..." : "Generate Context"}
                    </Button>
                    <Button onClick={handleSave} disabled={saving || !selectedTable}>
                        <Save className="h-4 w-4 mr-2" />
                        {saving ? "Saving..." : "Save"}
                    </Button>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Table List Sidebar */}
                <div className="w-64 border-r overflow-y-auto p-4">
                    <h2 className="font-semibold mb-3">Tables</h2>
                    <div className="space-y-1">
                        {tables.map((table) => {
                            const hasModel = models.some(m => m.table_name === table.name);
                            return (
                                <button
                                    key={table.name}
                                    onClick={() => setSelectedTable(table.name)}
                                    className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${selectedTable === table.name
                                        ? "bg-primary text-primary-foreground"
                                        : "hover:bg-muted"
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="truncate">{table.name}</span>
                                        {hasModel && <Badge variant="secondary" className="text-xs">✓</Badge>}
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Editor Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {selectedTableData ? (
                        <div className="max-w-4xl space-y-6">
                            <Tabs defaultValue="description" className="w-full">
                                <TabsList>
                                    <TabsTrigger value="description">Description</TabsTrigger>
                                    <TabsTrigger value="columns">Columns</TabsTrigger>
                                    <TabsTrigger value="prompt">System Prompt</TabsTrigger>
                                    <TabsTrigger value="glossary">Business Glossary</TabsTrigger>
                                </TabsList>

                                <TabsContent value="description" className="space-y-4">
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Business Description</CardTitle>
                                            <CardDescription>
                                                Describe what this table represents in business terms
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            <Textarea
                                                value={businessDescription}
                                                onChange={(e) => setBusinessDescription(e.target.value)}
                                                placeholder="e.g., This table stores customer information including contact details and account status..."
                                                rows={6}
                                            />
                                        </CardContent>
                                    </Card>
                                </TabsContent>

                                <TabsContent value="columns" className="space-y-4">
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Column Descriptions</CardTitle>
                                            <CardDescription>
                                                Add business-friendly descriptions for each column
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent className="space-y-4">
                                            {selectedTableData.columns.map((col) => (
                                                <div key={col.name} className="space-y-2">
                                                    <Label>
                                                        {col.name} <Badge variant="outline" className="ml-2">{col.type}</Badge>
                                                    </Label>
                                                    <Input
                                                        value={columnDescriptions[col.name] || ""}
                                                        onChange={(e) => setColumnDescriptions({
                                                            ...columnDescriptions,
                                                            [col.name]: e.target.value
                                                        })}
                                                        placeholder="Describe what this column represents..."
                                                    />
                                                </div>
                                            ))}
                                        </CardContent>
                                    </Card>
                                </TabsContent>

                                <TabsContent value="prompt" className="space-y-4">
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Custom System Prompt</CardTitle>
                                            <CardDescription>
                                                Define how the AI agent should understand this table
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            <Textarea
                                                value={systemPrompt}
                                                onChange={(e) => setSystemPrompt(e.target.value)}
                                                placeholder="You are analyzing customer data. This table contains..."
                                                rows={10}
                                                className="font-mono text-sm"
                                            />
                                        </CardContent>
                                    </Card>
                                </TabsContent>

                                <TabsContent value="glossary" className="space-y-4">
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Business Glossary</CardTitle>
                                            <CardDescription>
                                                Define business terms and their meanings
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent className="space-y-4">
                                            <div className="flex gap-2">
                                                <Input
                                                    value={newGlossaryTerm}
                                                    onChange={(e) => setNewGlossaryTerm(e.target.value)}
                                                    placeholder="Term (e.g., MRR)"
                                                />
                                                <Input
                                                    value={newGlossaryDef}
                                                    onChange={(e) => setNewGlossaryDef(e.target.value)}
                                                    placeholder="Definition"
                                                />
                                                <Button onClick={handleAddGlossaryTerm}>Add</Button>
                                            </div>
                                            <div className="space-y-2">
                                                {Object.entries(businessGlossary).map(([term, def]) => (
                                                    <div key={term} className="p-3 border rounded-lg">
                                                        <div className="font-semibold">{term}</div>
                                                        <div className="text-sm text-muted-foreground">{def}</div>
                                                    </div>
                                                ))}
                                            </div>
                                        </CardContent>
                                    </Card>
                                </TabsContent>
                            </Tabs>
                        </div>
                    ) : (
                        <div className="flex items-center justify-center h-full">
                            <p className="text-muted-foreground">Select a table to edit its semantic model</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
