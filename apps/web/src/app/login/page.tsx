"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email("Enter a valid clinic email."),
  password: z.string().min(8, "Password must be at least 8 characters.")
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage(): JSX.Element {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string>("");
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormValues>({
    defaultValues: { email: "", password: "" }
  });

  const onSubmit = async (values: LoginFormValues): Promise<void> => {
    setSubmitError("");
    const validation = loginSchema.safeParse(values);
    if (!validation.success) {
      validation.error.issues.forEach((issue) => {
        const field = issue.path[0];
        if (field === "email" || field === "password") {
          setError(field, { type: "manual", message: issue.message });
        }
      });
      return;
    }

    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(validation.data)
    });
    const data = (await response.json()) as { success: boolean; error?: string };
    if (!response.ok || !data.success) {
      setSubmitError(data.error ?? "Login failed. Please check your credentials.");
      return;
    }
    const redirect =
      typeof window !== "undefined"
        ? new URLSearchParams(window.location.search).get("redirect") || "/dashboard"
        : "/dashboard";
    router.replace(redirect);
    router.refresh();
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-light via-surface to-white px-4 py-10">
      <section className="w-full max-w-md rounded-2xl border border-primary/20 bg-white p-8 shadow-lg">
        <p className="font-heading text-sm font-semibold uppercase tracking-wider text-primary">
          Staff Portal
        </p>
        <h1 className="mt-2 font-heading text-3xl font-semibold text-slate-900">Clinic Dashboard Login</h1>
        <p className="mt-2 text-sm text-muted">
          Sign in with your staff account to manage appointments and live conversations.
        </p>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit(onSubmit)}>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              {...register("email")}
            />
            {errors.email ? <p className="mt-1 text-xs text-error">{errors.email.message}</p> : null}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              {...register("password")}
            />
            {errors.password ? (
              <p className="mt-1 text-xs text-error">{errors.password.message}</p>
            ) : null}
          </div>

          {submitError ? <p className="rounded-md bg-error/10 p-2 text-sm text-error">{submitError}</p> : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-primary px-3 py-2.5 text-sm font-semibold text-white transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
