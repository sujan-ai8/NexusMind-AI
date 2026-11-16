import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { AlertCircle, ArrowRight, Layers, Lock, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { apiRequest } from "@/lib/api-client";
import { useAuth } from "@/contexts/AuthContext";
import { useWorkspace } from "@/contexts/WorkspaceContext";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginPage() {
  const { login } = useAuth();
  const { refreshWorkspaces } = useWorkspace();
  const navigate = useNavigate();
  const location = useLocation();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "admin@nexusmind.ai",
      password: "NexusAdmin@2026",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsLoading(true);
      setErrorMessage(null);

      const res = await apiRequest<{
        user: any;
        token: { access_token: string };
      }>("/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      });

      login(res.token.access_token, res.user);

      // Check if user has workspaces
      const workspaces = await refreshWorkspaces();
      if (workspaces.length === 0) {
        navigate("/onboarding");
      } else {
        const from = (location.state as any)?.from?.pathname || "/dashboard";
        navigate(from, { replace: true });
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Invalid email or password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12 selection:bg-primary/20 selection:text-primary">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <Link to="/" className="inline-flex items-center gap-2 mb-2">
            <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <Layers className="w-6 h-6" />
            </div>
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Sign in to NexusMind AI</h1>
          <p className="text-sm text-muted-foreground">
            Access your cloud intelligence workspace and telemetry pipelines
          </p>
        </div>

        <Card className="border-border shadow-xl">
          <CardHeader className="pb-4">
            <CardTitle className="text-base">Enter Credentials</CardTitle>
            <CardDescription className="text-xs">
              Pre-filled with seeded administrator credentials for instant Phase 1 evaluation.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {errorMessage && (
              <div className="mb-4 flex items-center gap-2 p-3 text-xs rounded-md bg-destructive/10 border border-destructive/20 text-destructive">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-muted-foreground" /> Email Address
                </label>
                <Input
                  type="email"
                  placeholder="engineer@enterprise.com"
                  autoComplete="email"
                  {...register("email")}
                />
                {errors.email && (
                  <p className="text-[11px] text-destructive">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-muted-foreground" /> Password
                </label>
                <Input
                  type="password"
                  placeholder="••••••••"
                  autoComplete="current-password"
                  {...register("password")}
                />
                {errors.password && (
                  <p className="text-[11px] text-destructive">{errors.password.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full mt-2" isLoading={isLoading}>
                Sign In
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </form>
          </CardContent>
          <CardFooter className="pt-2 border-t border-border flex justify-between text-xs text-muted-foreground">
            <span>Don't have an account?</span>
            <Link to="/register" className="font-semibold text-primary hover:underline">
              Register here
            </Link>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}

