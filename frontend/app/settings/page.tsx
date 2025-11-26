"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Settings, Plus, Trash2, CheckCircle, XCircle, Loader2 } from "lucide-react";

interface LLMConfig {
    id: number;
    provider: string;
    model_name: string;
    is_active: boolean;
}

export default function SettingsPage() {
    const [configs, setConfigs] = useState<LLMConfig[]>([]);
    const [loading, setLoading] = useState(true);
    const [showNewConfig, setShowNewConfig] = useState(false);
    const [testing, setTesting] = useState<number | null>(null);

    const [newConfig, setNewConfig] = useState({
        provider: "openai",
        model_name: "gpt-4",
        api_key: "",
        is_active: false
    });

    useEffect(() => {
        fetchConfigs();
    }, []);

    const fetchConfigs = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/v1/admin/llm-configs");
            if (response.ok) {
                const data = await response.json();
                setConfigs(data);
            }
        } catch (error) {
            console.error("Error fetching configs:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddConfig = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/v1/admin/llm-config", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newConfig)
            });

            if (response.ok) {
                await fetchConfigs();
                setShowNewConfig(false);
                setNewConfig({
                    provider: "openai",
                    model_name: "gpt-4",
                    api_key: "",
                    is_active: false
                });
            }
        } catch (error) {
            console.error("Error adding config:", error);
        }
    };

    const handleDeleteConfig = async (id: number) => {
        if (!confirm("Are you sure you want to delete this configuration?")) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/v1/admin/llm-config/${id}`, {
                method: "DELETE"
            });

            if (response.ok) {
                await fetchConfigs();
            }
        } catch (error) {
            console.error("Error deleting config:", error);
        }
    };

    const handleActivateConfig = async (id: number) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/v1/admin/llm-config/${id}/activate`, {
                method: "POST"
            });

            if (response.ok) {
                await fetchConfigs();
            }
        } catch (error) {
            console.error("Error activating config:", error);
        }
    };

    const handleTestConfig = async (id: number) => {
        setTesting(id);
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/v1/admin/llm-config/${id}/test`, {
                method: "POST"
            });

            if (response.ok) {
                const data = await response.json();
                alert(`✅ ${data.message}`);
            } else {
                const error = await response.json();
                alert(`❌ Test failed: ${error.detail}`);
            }
        } catch (error) {
            alert(`❌ Test failed: ${error}`);
        } finally {
            setTesting(null);
        }
    };

    const providerModels = {
        openai: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        anthropic: ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        google: ["gemini-pro", "gemini-pro-vision"],
        azure: ["gpt-4", "gpt-35-turbo"]
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            <div className="border-b px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Settings className="h-6 w-6" />
                    <h1 className="text-2xl font-bold">Settings</h1>
                </div>
            </div>

            <div className="flex-1 overflow-auto p-6">
                <div className="max-w-4xl space-y-6">
                    {/* LLM Configuration */}
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle>LLM Configuration</CardTitle>
                                    <CardDescription>
                                        Manage your AI provider settings and API keys
                                    </CardDescription>
                                </div>
                                <Button onClick={() => setShowNewConfig(true)}>
                                    <Plus className="h-4 w-4 mr-2" />
                                    Add Provider
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {configs.length === 0 ? (
                                <div className="text-center py-8 text-muted-foreground">
                                    <Settings className="h-12 w-12 mx-auto mb-2 opacity-50" />
                                    <p>No LLM providers configured</p>
                                    <p className="text-sm mt-1">Add a provider to enable AI features</p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {configs.map((config) => (
                                        <div
                                            key={config.id}
                                            className="flex items-center justify-between p-4 border rounded-lg"
                                        >
                                            <div className="flex items-center gap-4">
                                                <div className="flex flex-col">
                                                    <div className="flex items-center gap-2">
                                                        <h3 className="font-medium capitalize">{config.provider}</h3>
                                                        {config.is_active && (
                                                            <Badge variant="default">Active</Badge>
                                                        )}
                                                    </div>
                                                    <p className="text-sm text-muted-foreground">{config.model_name}</p>
                                                </div>
                                            </div>
                                            <div className="flex gap-2">
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleTestConfig(config.id)}
                                                    disabled={testing === config.id}
                                                >
                                                    {testing === config.id ? (
                                                        <Loader2 className="h-4 w-4 animate-spin" />
                                                    ) : (
                                                        "Test"
                                                    )}
                                                </Button>
                                                {!config.is_active && (
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => handleActivateConfig(config.id)}
                                                    >
                                                        <CheckCircle className="h-4 w-4 mr-1" />
                                                        Activate
                                                    </Button>
                                                )}
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleDeleteConfig(config.id)}
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* New Config Form */}
                            {showNewConfig && (
                                <Card className="border-2 border-primary">
                                    <CardHeader>
                                        <CardTitle>Add LLM Provider</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div className="grid gap-4 md:grid-cols-2">
                                            <div className="space-y-2">
                                                <Label>Provider</Label>
                                                <Select
                                                    value={newConfig.provider}
                                                    onValueChange={(value) => {
                                                        setNewConfig({
                                                            ...newConfig,
                                                            provider: value,
                                                            model_name: providerModels[value as keyof typeof providerModels][0]
                                                        });
                                                    }}
                                                >
                                                    <SelectTrigger>
                                                        <SelectValue />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        <SelectItem value="openai">OpenAI</SelectItem>
                                                        <SelectItem value="anthropic">Anthropic</SelectItem>
                                                        <SelectItem value="google">Google</SelectItem>
                                                        <SelectItem value="azure">Azure OpenAI</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                            </div>
                                            <div className="space-y-2">
                                                <Label>Model</Label>
                                                <Select
                                                    value={newConfig.model_name}
                                                    onValueChange={(value) => setNewConfig({ ...newConfig, model_name: value })}
                                                >
                                                    <SelectTrigger>
                                                        <SelectValue />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        {providerModels[newConfig.provider as keyof typeof providerModels].map((model) => (
                                                            <SelectItem key={model} value={model}>
                                                                {model}
                                                            </SelectItem>
                                                        ))}
                                                    </SelectContent>
                                                </Select>
                                            </div>
                                        </div>
                                        <div className="space-y-2">
                                            <Label>API Key</Label>
                                            <Input
                                                type="password"
                                                placeholder="sk-..."
                                                value={newConfig.api_key}
                                                onChange={(e) => setNewConfig({ ...newConfig, api_key: e.target.value })}
                                            />
                                            <p className="text-xs text-muted-foreground">
                                                Your API key will be encrypted and stored securely
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <input
                                                type="checkbox"
                                                id="is-active"
                                                checked={newConfig.is_active}
                                                onChange={(e) => setNewConfig({ ...newConfig, is_active: e.target.checked })}
                                            />
                                            <Label htmlFor="is-active">Set as active provider</Label>
                                        </div>
                                        <div className="flex gap-2">
                                            <Button onClick={handleAddConfig}>Add Provider</Button>
                                            <Button variant="outline" onClick={() => setShowNewConfig(false)}>
                                                Cancel
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>
                            )}
                        </CardContent>
                    </Card>

                    {/* Info Card */}
                    <Card>
                        <CardHeader>
                            <CardTitle>About LLM Providers</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2 text-sm text-muted-foreground">
                            <p>• <strong>OpenAI</strong>: GPT-4 and GPT-3.5 models for general-purpose AI</p>
                            <p>• <strong>Anthropic</strong>: Claude models with enhanced reasoning capabilities</p>
                            <p>• <strong>Google</strong>: Gemini models with multimodal capabilities</p>
                            <p>• <strong>Azure OpenAI</strong>: Enterprise-grade OpenAI models</p>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
