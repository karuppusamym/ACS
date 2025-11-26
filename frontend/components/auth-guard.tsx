"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import apiClient from "@/lib/api-client";

const PUBLIC_PATHS = new Set(["/login", "/register"]);

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    async function check() {
      // Skip auth check for public pages
      if (PUBLIC_PATHS.has(pathname || "/")) {
        setChecked(true);
        return;
      }

      try {
        await apiClient.auth.getCurrentUser();
        setChecked(true);
      } catch (err) {
        // Not authenticated → redirect to login
        router.replace("/login");
      }
    }

    check();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  if (!checked) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-sm text-muted-foreground">Loading…</div>
      </div>
    );
  }

  return <>{children}</>;
}
