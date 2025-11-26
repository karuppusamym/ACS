import { cn } from "@/lib/utils";

interface MessageBubbleProps {
    message: {
        role: "user" | "assistant";
        content: string;
        timestamp: Date;
    };
}

export function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === "user";

    return (
        <div
            className={cn(
                "flex w-full",
                isUser ? "justify-end" : "justify-start"
            )}
        >
            <div
                className={cn(
                    "max-w-[80%] rounded-lg px-4 py-2",
                    isUser
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                )}
            >
                <p className="text-sm">{message.content}</p>
                <span className="mt-1 block text-xs opacity-50">
                    {message.timestamp.toLocaleTimeString()}
                </span>
            </div>
        </div>
    );
}
