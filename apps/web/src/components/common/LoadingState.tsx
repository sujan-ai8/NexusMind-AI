import React from "react";

export function LoadingState({ message = "Loading intelligence modules..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] w-full p-8 text-center">
      <div className="relative w-12 h-12 mb-4">
        <div className="absolute inset-0 rounded-full border-2 border-primary/20 animate-ping"></div>
        <div className="w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
      </div>
      <p className="text-sm font-medium text-muted-foreground">{message}</p>
    </div>
  );
}

