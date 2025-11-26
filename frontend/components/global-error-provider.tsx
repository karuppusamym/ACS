"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useToast } from "@/components/ui/use-toast";

interface GlobalErrorContextType {
    showError: (message: string) => void;
}

const GlobalErrorContext = createContext<GlobalErrorContextType | undefined>(undefined);

export function GlobalErrorProvider({ children }: { children: React.ReactNode }) {
    const { toast } = useToast();

    const showError = (message: string) => {
        toast({
            title: "Error",
            description: message,
            variant: "destructive",
        });
    };

    // Listen for unhandled promise rejections (often network errors)
    useEffect(() => {
        const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
            // Check if it's a fetch error
            if (event.reason instanceof TypeError && event.reason.message === "Failed to fetch") {
                showError("Unable to connect to the server. Please check your internet connection or try again later.");
            }
        };

        window.addEventListener("unhandledrejection", handleUnhandledRejection);

        return () => {
            window.removeEventListener("unhandledrejection", handleUnhandledRejection);
        };
    }, [toast]);

    return (
        <GlobalErrorContext.Provider value={{ showError }}>
            {children}
        </GlobalErrorContext.Provider>
    );
}

export function useGlobalError() {
    const context = useContext(GlobalErrorContext);
    if (!context) {
        throw new Error("useGlobalError must be used within a GlobalErrorProvider");
    }
    return context;
}
