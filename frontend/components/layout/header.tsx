export function Header() {
    return (
        <header className="flex h-14 items-center gap-4 border-b bg-background px-6">
            <div className="flex flex-1 items-center justify-between">
                <h1 className="text-lg font-semibold">Dashboard</h1>
                <div className="flex items-center gap-4">
                    {/* Add UserNav or other header items here */}
                    <div className="h-8 w-8 rounded-full bg-muted" />
                </div>
            </div>
        </header>
    );
}
