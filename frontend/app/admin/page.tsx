"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Trash2 } from "lucide-react";

interface LLMConfig {
    id: string;
    provider: string;
    model_name: string;
    api_key: string;
    is_active: boolean;
}

export default function AdminPage() {
    const [llmConfigs, setLlmConfigs] = useState<LLMConfig[]>([]);
    const [newConfig, setNewConfig] = useState({
        provider: "openai",
        model_name: "gpt-4",
        api_key: "",
    });
    const [storagePath, setStoragePath] = useState("./data/uploads");
    const [allowedExtensions, setAllowedExtensions] = useState(".csv,.xlsx,.json,.parquet");

    const handleAddLLMConfig = () => {
        const config: LLMConfig = {
            id: Date.now().toString(),
            ...newConfig,
            is_active: llmConfigs.length === 0, // First one is active by default
        };
        setLlmConfigs([...llmConfigs, config]);
        setNewConfig({ provider: "openai", model_name: "gpt-4", api_key: "" });
    };

    const handleRemoveConfig = (id: string) => {
        setLlmConfigs(llmConfigs.filter((c) => c.id !== id));
    };

    const handleSaveStorage = () => {
        // TODO: Call API to save storage config
        alert("Storage configuration saved!");
    };

    return (
        <div className="h-full flex flex-col">
            <div className="flex items-center justify-between border-b px-6 py-4">
                <h1 className="text-2xl font-bold">Admin Settings</h1>
            </div>
            <div className="flex-1 overflow-auto p-6">
                <div className="max-w-4xl space-y-6">
                    {/* LLM Configuration */}
                    <Card>
                        <CardHeader>
                            <CardTitle>LLM Configuration</CardTitle>
                            <CardDescription>
                                Configure which LLM models are available for analysis. The active model will be used for query generation.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Existing Configurations */}
                            {llmConfigs.length > 0 && (
                                <div className="space-y-3">
                                    <h3 className="text-sm font-medium">Configured Models</h3>
                                    {llmConfigs.map((config) => (
                                        <div key={config.id} className="flex items-center gap-3 rounded-lg border p-3">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-medium">{config.provider}</span>
                                                    <span className="text-sm text-muted-foreground">•</span>
                                                    <span className="text-sm">{config.model_name}</span>
                                                    {config.is_active && (
                                                        <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700">
                                                            Active
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="text-xs text-muted-foreground mt-1">
                                                    API Key: {config.api_key.substring(0, 8)}...
                                                </div>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => handleRemoveConfig(config.id)}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Add New Configuration */}
                            <div className="space-y-3 rounded-lg border p-4">
                                <h3 className="text-sm font-medium">Add New Model</h3>
                                <div className="grid gap-3">
                                    <div className="grid gap-2">
                                        <Label htmlFor="provider">Provider</Label>
                                        <Select
                                            value={newConfig.provider}
                                            onValueChange={(value) => setNewConfig({ ...newConfig, provider: value })}
                                        >
                                            <SelectTrigger id="provider">
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="openai">OpenAI</SelectItem>
                                                <SelectItem value="anthropic">Anthropic</SelectItem>
                                                <SelectItem value="google">Google (Gemini)</SelectItem>
                                                <SelectItem value="azure">Azure OpenAI</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="model">Model Name</Label>
                                        <Input
                                            id="model"
                                            placeholder="e.g., gpt-4, claude-3-opus"
                                            value={newConfig.model_name}
                                            onChange={(e) => setNewConfig({ ...newConfig, model_name: e.target.value })}
                                        />
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="apikey">API Key</Label>
                                        <Input
                                            id="apikey"
                                            type="password"
                                            placeholder="sk-..."
                                            value={newConfig.api_key}
                                            onChange={(e) => setNewConfig({ ...newConfig, api_key: e.target.value })}
                                        />
                                    </div>
                                    <Button onClick={handleAddLLMConfig} className="w-full">
                                        <Plus className="mr-2 h-4 w-4" />
                                        Add Model
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Storage Configuration */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Default Storage</CardTitle>
                            <CardDescription>
                                Configure default storage location for uploaded files and allowed file extensions.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-2">
                                <Label htmlFor="storage-path">Storage Path</Label>
                                <Input
                                    id="storage-path"
                                    placeholder="./data/uploads"
                                    value={storagePath}
                                    onChange={(e) => setStoragePath(e.target.value)}
                                />
                                <p className="text-xs text-muted-foreground">
                                    Relative or absolute path where uploaded files will be stored
                                </p>
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="extensions">Allowed Extensions</Label>
                                <Textarea
                                    id="extensions"
                                    placeholder=".csv,.xlsx,.json,.parquet"
                                    value={allowedExtensions}
                                    onChange={(e) => setAllowedExtensions(e.target.value)}
                                    rows={3}
                                />
                                <p className="text-xs text-muted-foreground">
                                    Comma-separated list of allowed file extensions
                                </p>
                            </div>
                            <Button onClick={handleSaveStorage}>Save Storage Configuration</Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
