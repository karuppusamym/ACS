import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { Providers } from "@/components/providers";
import { AuthGuard } from "@/components/auth-guard";
import { ToastProvider } from "@/components/ui/use-toast";
import { GlobalErrorProvider } from "@/components/global-error-provider";
import { ErrorBoundary } from "@/components/error-boundary";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Agentic Data Analyst",
  description: "AI-powered data analysis platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ErrorBoundary>
          <Providers>
            <ToastProvider>
              <GlobalErrorProvider>
                <AuthGuard>
                  <div className="flex h-screen overflow-hidden">
                    <Sidebar />
                    <div className="flex flex-col flex-1 overflow-hidden">
                      <Header />
                      <main className="flex-1 overflow-auto bg-gray-50">
                        <ErrorBoundary>{children}</ErrorBoundary>
                      </main>
                    </div>
                  </div>
                </AuthGuard>
              </GlobalErrorProvider>
            </ToastProvider>
          </Providers>
        </ErrorBoundary>
      </body>
    </html>
  );
}
