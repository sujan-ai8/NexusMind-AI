import React from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Cloud,
  Cpu,
  Database,
  FolderKanban,
  Globe,
  Layers,
  Lock,
  Moon,
  Server,
  Shield,
  Sparkles,
  Sun,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useTheme } from "@/contexts/ThemeContext";

export function LandingPage() {
  const { theme, toggleTheme } = useTheme();

  const capabilities = [
    {
      title: "Software Project Management",
      desc: "Comprehensive agile tracking, sprint planning, risk matrices, and task kanban workflows.",
      icon: FolderKanban,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
      pill: "Pillar 1",
    },
    {
      title: "Big Data Analytics",
      desc: "Petabyte-scale workload profiling, statistical telemetry characterization, and anomaly clustering.",
      icon: Database,
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
      pill: "Pillar 2",
    },
    {
      title: "Generative AI",
      desc: "Autonomous conversational operations assistant offering root-cause diagnosis and executive reporting.",
      icon: Bot,
      color: "text-purple-500",
      bg: "bg-purple-500/10",
      pill: "Pillar 3",
    },
    {
      title: "Reinforcement Learning",
      desc: "Closed-loop policy optimization (PPO) balancing cost reduction against strict application SLAs.",
      icon: Activity,
      color: "text-amber-500",
      bg: "bg-amber-500/10",
      pill: "Pillar 4",
    },
    {
      title: "Advanced Machine Learning",
      desc: "Multi-horizon deep learning demand forecasting with ARIMA, Prophet, and LSTM neural architectures.",
      icon: BrainCircuit,
      color: "text-cyan-500",
      bg: "bg-cyan-500/10",
      pill: "Pillar 5",
    },
    {
      title: "AWS Cloud Computing",
      desc: "Enterprise cloud integration spanning EC2, EKS, Aurora PostgreSQL, S3, and CloudWatch telemetry.",
      icon: Cloud,
      color: "text-orange-500",
      bg: "bg-orange-500/10",
      pill: "Pillar 6",
    },
  ];

  const features = [
    {
      title: "Cloud Workload Analytics",
      desc: "Continuously characterize CPU, memory, network I/O, and storage patterns across multi-node clusters.",
      icon: Cpu,
    },
    {
      title: "Predictive Intelligence",
      desc: "Forecast compute bottlenecks and traffic spikes hours in advance to pre-scale infrastructure seamlessly.",
      icon: Zap,
    },
    {
      title: "Resource Optimization",
      desc: "Eliminate idle compute waste and right-size over-provisioned instances with mathematical guarantees.",
      icon: BarChart3,
    },
    {
      title: "AI-Powered Insights",
      desc: "Synthesize complex multi-variable cluster telemetry into plain-language executive summaries and alerts.",
      icon: Sparkles,
    },
    {
      title: "Cloud-Native Architecture",
      desc: "Built on containerized microservices, scalable async queues, and decoupled REST API micro-gateways.",
      icon: Server,
    },
    {
      title: "Enterprise Security",
      desc: "Strict multi-tenant workspace isolation, role-based access control (RBAC), and audited API telemetry.",
      icon: Lock,
    },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col selection:bg-primary/20 selection:text-primary">
      {/* 1. Navigation Header */}
      <nav className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <Layers className="w-5 h-5 text-primary" />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-extrabold tracking-tight bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
                NexusMind AI
              </span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-widest font-mono">
                Cloud Intelligence
              </span>
            </div>
          </Link>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-6 text-sm font-medium text-muted-foreground">
            <a href="#product" className="hover:text-foreground transition-colors">Product</a>
            <a href="#features" className="hover:text-foreground transition-colors">Features</a>
            <a href="#platform" className="hover:text-foreground transition-colors">Platform</a>
            <a href="#documentation" className="hover:text-foreground transition-colors">Documentation</a>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              title="Toggle theme"
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <Link to="/login">
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link to="/register">
              <Button variant="primary" size="sm" className="shadow-md shadow-primary/20">
                Get Started
                <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* 2. Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-24 md:pt-28 md:pb-32">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(59,130,246,0.15),rgba(255,255,255,0))] dark:bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(59,130,246,0.22),rgba(11,15,25,0))]"></div>

        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Badge variant="secondary" className="mb-6 px-3.5 py-1 text-xs font-semibold gap-1.5 border border-primary/20 bg-primary/10 text-primary">
            <Sparkles className="w-3.5 h-3.5" />
            Phase 1 Enterprise Foundation & Architecture Active
          </Badge>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-foreground max-w-4xl mx-auto leading-[1.12]">
            Intelligent Cloud Operations.{" "}
            <span className="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 bg-clip-text text-transparent">
              Powered by AI.
            </span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Analyze cloud workloads, forecast infrastructure demand, and explore intelligent resource optimization through a unified cloud intelligence platform.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" className="h-12 px-8 text-base shadow-lg shadow-primary/25 font-semibold">
                Get Started
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <a href="#product">
              <Button variant="outline" size="lg" className="h-12 px-8 text-base">
                Explore Platform
              </Button>
            </a>
          </div>

          {/* Premium Product Preview Visual (Labeled strictly as demo preview) */}
          <div className="mt-16 relative mx-auto max-w-5xl rounded-xl border border-border bg-card/60 p-2 sm:p-4 shadow-2xl backdrop-blur-xl">
            <div className="flex items-center justify-between pb-3 px-3 border-b border-border text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                <span className="ml-2 font-mono text-[11px] text-foreground/80">nexusmind.internal/dashboard/preview</span>
              </div>
              <Badge variant="demo">PRODUCT DEMO PREVIEW — SIMULATED METRICS</Badge>
            </div>

            <div className="p-4 sm:p-6 text-left space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-lg border border-border bg-background/50">
                  <div className="text-[11px] text-muted-foreground">Avg CPU Utilization</div>
                  <div className="text-xl font-bold text-foreground mt-1">43.8%</div>
                  <div className="text-[10px] text-emerald-500 font-semibold mt-0.5">↓ 4.2% optimized</div>
                </div>
                <div className="p-3 rounded-lg border border-border bg-background/50">
                  <div className="text-[11px] text-muted-foreground">Memory Allocated</div>
                  <div className="text-xl font-bold text-foreground mt-1">68.2%</div>
                  <div className="text-[10px] text-blue-500 font-semibold mt-0.5">Optimal headroom</div>
                </div>
                <div className="p-3 rounded-lg border border-border bg-background/50">
                  <div className="text-[11px] text-muted-foreground">Workload Volume</div>
                  <div className="text-xl font-bold text-foreground mt-1">142.5k</div>
                  <div className="text-[10px] text-muted-foreground font-semibold mt-0.5">req/min</div>
                </div>
                <div className="p-3 rounded-lg border border-border bg-background/50">
                  <div className="text-[11px] text-muted-foreground">Monthly Run Rate</div>
                  <div className="text-xl font-bold text-foreground mt-1">$1,248</div>
                  <div className="text-[10px] text-emerald-500 font-semibold mt-0.5">↓ 8.6% saved</div>
                </div>
              </div>

              {/* Decorative Mock Chart Line */}
              <div className="p-4 rounded-lg border border-border bg-background/50 space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold text-muted-foreground">
                  <span>Workload Telemetry Simulation Trace</span>
                  <span className="font-mono text-[10px] text-primary">AWS us-east-1 Cluster</span>
                </div>
                <div className="h-20 w-full flex items-end gap-1.5 pt-4">
                  {[35, 42, 55, 68, 72, 60, 48, 52, 65, 80, 75, 62, 54, 46, 50, 68, 74, 58, 44, 48].map((val, idx) => (
                    <div
                      key={idx}
                      className="flex-1 bg-gradient-to-t from-primary/30 to-primary rounded-t-sm transition-all hover:bg-primary"
                      style={{ height: `${val}%` }}
                      title={`Time window ${idx}: ${val}% load`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Platform Overview: The Six Capabilities */}
      <section id="platform" className="py-20 border-t border-border bg-card/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge variant="secondary" className="mb-3 text-xs font-semibold">
              Comprehensive Platform Capabilities
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
              Six Pillars of Cloud Intelligence
            </h2>
            <p className="mt-3 text-muted-foreground">
              NexusMind AI unites Software Project Management, Big Data Analytics, Generative AI, Reinforcement Learning, Advanced Machine Learning, and AWS Cloud Computing into a single cohesive architecture.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {capabilities.map((cap) => {
              const Icon = cap.icon;
              return (
                <div
                  key={cap.title}
                  className="rounded-xl border border-border bg-card p-6 transition-all hover:border-primary/40 hover:shadow-md flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-10 h-10 rounded-lg ${cap.bg} ${cap.color} flex items-center justify-center`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-muted text-muted-foreground">
                        {cap.pill}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-foreground mb-2">{cap.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{cap.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 4. Features Section */}
      <section id="features" className="py-20 border-t border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge variant="secondary" className="mb-3 text-xs font-semibold">
              Engineered for Enterprise Scale
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
              Architectural Highlights
            </h2>
            <p className="mt-3 text-muted-foreground">
              A modern software project engineered with clean layer separation, multi-tier security, and cloud scalability.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feat) => {
              const Icon = feat.icon;
              return (
                <div key={feat.title} className="p-6 rounded-xl border border-border bg-card/60 space-y-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-semibold text-foreground">{feat.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{feat.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 5. Product & Documentation Section */}
      <section id="documentation" className="py-20 border-t border-border bg-muted/20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-2xl border border-border bg-card p-8 md:p-12 shadow-xl">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <Badge variant="secondary" className="mb-3 text-xs font-semibold">
                  MCA Final Year Project Architecture
                </Badge>
                <h2 className="text-3xl font-extrabold text-foreground">
                  Complete Software Project Management Deliverables
                </h2>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                  Phase 1 includes 12 comprehensive SPM governance documents, automated test suites, database migrations, and clean role-based authorization.
                </p>
                <div className="mt-6 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Project Charter</div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Scope Specification</div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Functional Specs</div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Non-Functional Specs</div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Work Breakdown (WBS)</div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Agile Sprint Plan</div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Milestone Plan</div>
                  <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Risk Register</div>
                </div>
              </div>
              <div className="bg-background rounded-xl border border-border p-5 space-y-3 font-mono text-xs">
                <div className="text-primary font-bold"># Local Development Quickstart</div>
                <div className="text-muted-foreground">$ git clone ... && cd "NexusMind AI"</div>
                <div className="text-muted-foreground">$ docker compose up --build -d</div>
                <div className="p-3 rounded-lg bg-card border border-border text-[11px] space-y-1">
                  <p className="text-emerald-500">✓ Web Frontend: http://localhost:3000</p>
                  <p className="text-blue-500">✓ FastAPI Core: http://localhost:8000</p>
                  <p className="text-purple-500">✓ Interactive API Docs: /docs</p>
                  <p className="text-amber-500">✓ PostgreSQL: port 5432</p>
                </div>
                <Link to="/register" className="block pt-2">
                  <Button className="w-full" variant="primary" size="sm">
                    Enter Application Now
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Footer */}
      <footer className="mt-auto border-t border-border bg-card py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8 text-xs">
            <div>
              <span className="font-semibold text-foreground uppercase tracking-wider">Product</span>
              <ul className="mt-3 space-y-2 text-muted-foreground">
                <li><Link to="/dashboard" className="hover:text-foreground">Live Dashboard</Link></li>
                <li><Link to="/workloads" className="hover:text-foreground">Workload Intelligence</Link></li>
                <li><Link to="/analytics" className="hover:text-foreground">Big Data Analytics</Link></li>
                <li><Link to="/models" className="hover:text-foreground">ML Models</Link></li>
              </ul>
            </div>
            <div>
              <span className="font-semibold text-foreground uppercase tracking-wider">Platform</span>
              <ul className="mt-3 space-y-2 text-muted-foreground">
                <li><Link to="/optimization" className="hover:text-foreground">RL Optimization</Link></li>
                <li><Link to="/copilot" className="hover:text-foreground">AI Copilot</Link></li>
                <li><Link to="/cloud" className="hover:text-foreground">AWS Cloud Services</Link></li>
                <li><Link to="/spm" className="hover:text-foreground">Agile SPM</Link></li>
              </ul>
            </div>
            <div>
              <span className="font-semibold text-foreground uppercase tracking-wider">Documentation</span>
              <ul className="mt-3 space-y-2 text-muted-foreground">
                <li><a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-foreground">API Reference</a></li>
                <li><Link to="/spm" className="hover:text-foreground">SPM Deliverables</Link></li>
                <li><a href="#documentation" className="hover:text-foreground">System Architecture</a></li>
                <li><Link to="/settings" className="hover:text-foreground">Security & RBAC</Link></li>
              </ul>
            </div>
            <div>
              <span className="font-semibold text-foreground uppercase tracking-wider">About</span>
              <ul className="mt-3 space-y-2 text-muted-foreground">
                <li><span className="text-foreground">NexusMind AI</span></li>
                <li><span>MCA Final-Year Industry Project</span></li>
                <li><span>Academic Year 2026</span></li>
                <li><span>Enterprise Cloud SaaS</span></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between text-xs text-muted-foreground gap-4">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-primary" />
              <span>© 2026 NexusMind AI Platform. All rights reserved. Phase 1 Release.</span>
            </div>
            <div className="flex items-center gap-6">
              <a href="#privacy" className="hover:text-foreground">Privacy Policy</a>
              <a href="#terms" className="hover:text-foreground">Terms of Service</a>
              <a href="#contact" className="hover:text-foreground">Contact & Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

