import Sidebar from "@/components/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen" style={{ background: 'var(--background)' }}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area - offset for sidebar */}
      <main className="ml-64 min-h-screen" style={{ background: 'var(--background)' }}>
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>

      {/* Animated Background Elements - Cyberpunk Style */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-purple-500/8 rounded-full blur-3xl animate-pulse delay-500" />
      </div>
    </div>
  );
}
