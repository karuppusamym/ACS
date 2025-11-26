"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { LogOut, User } from "lucide-react";
import apiClient from "@/lib/api-client";

export function Header() {
    const router = useRouter();

    const handleLogout = async () => {
        try {
            await apiClient.auth.logout();
            localStorage.removeItem("access_token");
            router.push("/login");
        } catch (error) {
            console.error("Logout failed:", error);
            // Force redirect even on error
            localStorage.removeItem("access_token");
            router.push("/login");
        }
    };

    return (
        <header className="flex h-14 items-center gap-4 border-b bg-background px-6">
            <div className="flex flex-1 items-center justify-between">
                <h1 className="text-lg font-semibold">Dashboard</h1>
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" className="rounded-full">
                        <User className="h-5 w-5" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={handleLogout}>
                        <LogOut className="h-4 w-4 mr-2" />
                        Logout
                    </Button>
                </div>
            </div>
        </header>
    );
}
