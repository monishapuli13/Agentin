import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <Card>
      <CardContent className="py-10 text-center">
        <p className="font-medium">{title}</p>
        {children ? <div className="mt-2 text-sm text-muted-foreground">{children}</div> : null}
      </CardContent>
    </Card>
  );
}

