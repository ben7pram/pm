"use client";

import { useState, useEffect } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";

export default function Home() {
  const [auth, setAuth] = useState<{ authenticated: boolean } | null>(null);

  useEffect(() => {
    fetch("/api/me", { cache: "no-store" })
      .then((r) => r.json())
      .then((data) => setAuth(data));
  }, []);

  if (auth === null) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  if (!auth.authenticated) {
    return <LoginForm onSuccess={() => setAuth({ authenticated: true })} />;
  }

  return <KanbanBoard />;
}
