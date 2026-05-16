"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export default function QueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 2,  // 2 minutes - don't refetch on every navigation
            gcTime: 1000 * 60 * 10,    // 10 minutes - keep in memory
            retry: 1,
            refetchOnWindowFocus: false, // don't refetch when switching tabs
          },
        },
      }),
  );
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
