import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { AlertCircle, ArrowRight, Layers, Lock, Mail, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { apiRequest } from "@/lib/api-client";
import { useAuth } from "@/contexts/AuthContext";

const registerSchema = z.object({
  full_name: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters long")
    .regex(/[A-Z]/, "Must include at least one uppercase letter")
    .regex(/[0-9]/, "Must include at least one digit"),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setIsLoading(true);
      setErrorMessage(null);

      const res = await apiRequest<{
        user: any;
        token: { access_token: string };
      }>("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      });

      login(res.token.access_token, res.user);
      navigate("/onboarding");
    } catch (err: any) {
      setErrorMessage(err.message || "Registration failed");
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
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Create your Account</h1>
          <p className="text-sm text-muted-foreground">
            Join NexusMind AI to start analyzing and optimizing cloud workloads
          </p>
        </div>

        <Card className="border-border shadow-xl">
          <CardHeader className="pb-4">
            <CardTitle className="text-base">User Registration</CardTitle>
            <CardDescription className="text-xs">
              All credentials are secured via bcrypt password hashing and tokenized JWT auth.
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
                  <User className="w-3.5 h-3.5 text-muted-foreground" /> Full Name
                </label>
                <Input
                  type="text"
                  placeholder="Alex Mercer"
                  {...register("full_name")}
                />
                {errors.full_name && (
                  <p className="text-[11px] text-destructive">{errors.full_name.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-muted-foreground" /> Work Email
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
                  placeholder="Min. 8 characters with 1 uppercase & 1 digit"
                  autoComplete="new-password"
                  {...register("password")}
                />
                {errors.password && (
                  <p className="text-[11px] text-destructive">{errors.password.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full mt-2" isLoading={isLoading}>
                Create Account & Continue
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </form>
          </CardContent>
          <CardFooter className="pt-2 border-t border-border flex justify-between text-xs text-muted-foreground">
            <span>Already have an account?</span>
            <Link to="/login" className="font-semibold text-primary hover:underline">
              Sign in here
            </Link>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}

