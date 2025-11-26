"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, FileText, Search, Database, Loader2 } from "lucide-react";

interface SearchResult {
    id: number;
    content: string;
    metadata: any;
    similarity: number;
}

export default function DocumentsPage() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [searching, setSearching] = useState(false);
    const [results, setResults] = useState<SearchResult[]>([]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("collection", "documents");

            const response = await fetch("http://127.0.0.1:8000/api/v1/documents/upload", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                },
                body: formData
            });

            if (response.ok) {
                alert("Document uploaded and embedded successfully!");
                setFile(null);
            } else {
                alert("Upload failed");
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            setUploading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;

        setSearching(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/v1/documents/search?query=${encodeURIComponent(searchQuery)}`, {
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setResults(data);
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            setSearching(false);
        }
    };

    return (
        <div className="h-screen flex flex-col">
            <div className="border-b px-6 py-4">
                <h1 className="text-2xl font-bold">Document Knowledge Base</h1>
                <p className="text-sm text-muted-foreground">Manage documents and perform semantic search</p>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
                <div className="grid gap-6 md:grid-cols-3">
                    {/* Upload Panel */}
                    <Card className="md:col-span-1">
                        <CardHeader>
                            <CardTitle>Upload Document</CardTitle>
                            <CardDescription>Add text documents to the knowledge base</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Document File (TXT/MD)</Label>
                                <div className="border-2 border-dashed rounded-lg p-4 text-center hover:bg-muted/50 transition-colors">
                                    <Input
                                        type="file"
                                        accept=".txt,.md"
                                        onChange={handleFileChange}
                                        className="hidden"
                                        id="doc-upload"
                                    />
                                    <Label htmlFor="doc-upload" className="cursor-pointer">
                                        <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                                        <span className="text-sm text-muted-foreground">
                                            {file ? file.name : "Click to upload"}
                                        </span>
                                    </Label>
                                </div>
                            </div>

                            <Button
                                className="w-full"
                                onClick={handleUpload}
                                disabled={!file || uploading}
                            >
                                {uploading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Uploading...
                                    </>
                                ) : (
                                    <>
                                        <Database className="mr-2 h-4 w-4" />
                                        Embed & Store
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>

                    {/* Search Panel */}
                    <div className="md:col-span-2 space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Semantic Search</CardTitle>
                                <CardDescription>Search documents using natural language</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="flex gap-2 mb-4">
                                    <Input
                                        placeholder="Ask a question or search for concepts..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                                    />
                                    <Button onClick={handleSearch} disabled={searching}>
                                        {searching ? (
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                        ) : (
                                            <Search className="h-4 w-4" />
                                        )}
                                    </Button>
                                </div>

                                <div className="space-y-4">
                                    {results.map((result) => (
                                        <Card key={result.id} className="bg-muted/30">
                                            <CardContent className="pt-4">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div className="flex items-center gap-2">
                                                        <FileText className="h-4 w-4 text-primary" />
                                                        <span className="font-medium text-sm">
                                                            {result.metadata.filename}
                                                        </span>
                                                    </div>
                                                    <span className="text-xs bg-primary/10 px-2 py-1 rounded text-primary">
                                                        {(result.similarity * 100).toFixed(1)}% match
                                                    </span>
                                                </div>
                                                <p className="text-sm text-muted-foreground line-clamp-3">
                                                    {result.content}
                                                </p>
                                            </CardContent>
                                        </Card>
                                    ))}

                                    {results.length === 0 && !searching && searchQuery && (
                                        <div className="text-center text-muted-foreground py-8">
                                            No relevant documents found
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
