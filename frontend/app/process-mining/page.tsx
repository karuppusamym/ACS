"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, FileText, Activity, GitBranch, Loader2, Play } from "lucide-react";

interface ProcessMetrics {
    cases: number;
    events: number;
    activities: number;
    variants: number;
}

interface ProcessStats {
    start_activities: Record<string, number>;
    end_activities: Record<string, number>;
    top_variants: Array<{ variant: string; count: number }>;
}

export default function ProcessMiningPage() {
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ metrics: ProcessMetrics; statistics: ProcessStats } | null>(null);
    const [columns, setColumns] = useState({
        case_id: "case_id",
        activity: "activity",
        timestamp: "timestamp"
    });

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;

        setLoading(true);
        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("case_id_col", columns.case_id);
            formData.append("activity_col", columns.activity);
            formData.append("timestamp_col", columns.timestamp);

            const response = await fetch("http://127.0.0.1:8000/api/v1/process/analyze", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                setResult(data);
            } else {
                console.error("Analysis failed");
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-screen flex flex-col">
            <div className="border-b px-6 py-4">
                <h1 className="text-2xl font-bold">Process Mining</h1>
                <p className="text-sm text-muted-foreground">Discover and analyze business processes from event logs</p>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
                <div className="grid gap-6 md:grid-cols-3">
                    {/* Configuration Panel */}
                    <Card className="md:col-span-1">
                        <CardHeader>
                            <CardTitle>Event Log Configuration</CardTitle>
                            <CardDescription>Upload CSV and map columns</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Event Log (CSV)</Label>
                                <div className="border-2 border-dashed rounded-lg p-4 text-center hover:bg-muted/50 transition-colors">
                                    <Input
                                        type="file"
                                        accept=".csv"
                                        onChange={handleFileChange}
                                        className="hidden"
                                        id="file-upload"
                                    />
                                    <Label htmlFor="file-upload" className="cursor-pointer">
                                        <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                                        <span className="text-sm text-muted-foreground">
                                            {file ? file.name : "Click to upload"}
                                        </span>
                                    </Label>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label>Case ID Column</Label>
                                <Input
                                    value={columns.case_id}
                                    onChange={(e) => setColumns({ ...columns, case_id: e.target.value })}
                                    placeholder="e.g., case_id"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Activity Column</Label>
                                <Input
                                    value={columns.activity}
                                    onChange={(e) => setColumns({ ...columns, activity: e.target.value })}
                                    placeholder="e.g., activity"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Timestamp Column</Label>
                                <Input
                                    value={columns.timestamp}
                                    onChange={(e) => setColumns({ ...columns, timestamp: e.target.value })}
                                    placeholder="e.g., timestamp"
                                />
                            </div>

                            <Button
                                className="w-full"
                                onClick={handleAnalyze}
                                disabled={!file || loading}
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <Play className="mr-2 h-4 w-4" />
                                        Analyze Process
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>

                    {/* Results Panel */}
                    <div className="md:col-span-2 space-y-6">
                        {result ? (
                            <>
                                {/* Metrics */}
                                <div className="grid grid-cols-4 gap-4">
                                    <Card>
                                        <CardContent className="pt-6 text-center">
                                            <div className="text-2xl font-bold">{result.metrics.cases}</div>
                                            <div className="text-xs text-muted-foreground">Cases</div>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardContent className="pt-6 text-center">
                                            <div className="text-2xl font-bold">{result.metrics.events}</div>
                                            <div className="text-xs text-muted-foreground">Events</div>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardContent className="pt-6 text-center">
                                            <div className="text-2xl font-bold">{result.metrics.activities}</div>
                                            <div className="text-xs text-muted-foreground">Activities</div>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardContent className="pt-6 text-center">
                                            <div className="text-2xl font-bold">{result.metrics.variants}</div>
                                            <div className="text-xs text-muted-foreground">Variants</div>
                                        </CardContent>
                                    </Card>
                                </div>

                                {/* Analysis Tabs */}
                                <Tabs defaultValue="variants">
                                    <TabsList>
                                        <TabsTrigger value="variants">
                                            <GitBranch className="mr-2 h-4 w-4" />
                                            Variants
                                        </TabsTrigger>
                                        <TabsTrigger value="activities">
                                            <Activity className="mr-2 h-4 w-4" />
                                            Activities
                                        </TabsTrigger>
                                        <TabsTrigger value="model">
                                            <FileText className="mr-2 h-4 w-4" />
                                            Process Model
                                        </TabsTrigger>
                                    </TabsList>

                                    <TabsContent value="variants">
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>Top Process Variants</CardTitle>
                                                <CardDescription>Most common execution paths</CardDescription>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="space-y-4">
                                                    {result.statistics.top_variants.map((variant, i) => (
                                                        <div key={i} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                                                            <div className="flex-1 mr-4">
                                                                <div className="text-sm font-medium mb-1">Variant {i + 1}</div>
                                                                <div className="text-xs text-muted-foreground font-mono">
                                                                    {variant.variant}
                                                                </div>
                                                            </div>
                                                            <div className="text-sm font-bold bg-primary/10 px-2 py-1 rounded">
                                                                {variant.count} cases
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    </TabsContent>

                                    <TabsContent value="activities">
                                        <div className="grid gap-4 md:grid-cols-2">
                                            <Card>
                                                <CardHeader>
                                                    <CardTitle>Start Activities</CardTitle>
                                                </CardHeader>
                                                <CardContent>
                                                    <div className="space-y-2">
                                                        {Object.entries(result.statistics.start_activities).map(([act, count]) => (
                                                            <div key={act} className="flex justify-between text-sm">
                                                                <span>{act}</span>
                                                                <span className="font-medium">{count}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </CardContent>
                                            </Card>
                                            <Card>
                                                <CardHeader>
                                                    <CardTitle>End Activities</CardTitle>
                                                </CardHeader>
                                                <CardContent>
                                                    <div className="space-y-2">
                                                        {Object.entries(result.statistics.end_activities).map(([act, count]) => (
                                                            <div key={act} className="flex justify-between text-sm">
                                                                <span>{act}</span>
                                                                <span className="font-medium">{count}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        </div>
                                    </TabsContent>

                                    <TabsContent value="model">
                                        <Card>
                                            <CardContent className="h-[400px] flex items-center justify-center text-muted-foreground">
                                                Process graph visualization would be rendered here using React Flow or Cytoscape
                                            </CardContent>
                                        </Card>
                                    </TabsContent>
                                </Tabs>
                            </>
                        ) : (
                            <div className="h-full flex items-center justify-center border-2 border-dashed rounded-lg text-muted-foreground">
                                <div className="text-center">
                                    <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                    <h3 className="text-lg font-medium">No Analysis Results</h3>
                                    <p>Upload an event log to see process insights</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
