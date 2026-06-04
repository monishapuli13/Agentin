"use client";

import { type ReactNode, useState } from "react";
import { cn } from "@/lib/utils";

export function Tabs({
  tabs,
  defaultValue
}: {
  tabs: Array<{ value: string; label: string; content: ReactNode }>;
  defaultValue?: string;
}) {
  const [active, setActive] = useState(defaultValue ?? tabs[0]?.value);
  return (
    <div className="space-y-4">
      <div className="inline-flex rounded-md border border-border bg-muted p-1">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            className={cn(
              "rounded-sm px-3 py-1.5 text-sm font-medium transition-colors",
              active === tab.value ? "bg-background shadow-sm" : "text-muted-foreground"
            )}
            onClick={() => setActive(tab.value)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.find((tab) => tab.value === active)?.content}
    </div>
  );
}

