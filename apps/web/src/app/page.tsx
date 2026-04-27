import ChatWidget from "@/components/chat/ChatWidget";

export default function HomePage(): JSX.Element {
  return (
    <>
      <main className="min-h-screen bg-surface p-6">
        <h1 className="font-heading text-3xl font-semibold text-slate-900">
          Autonomous Dental Appointment Bot
        </h1>
        <p className="mt-2 max-w-xl text-sm text-muted">
          Patient communication module initialized. The floating chat widget is available at the
          bottom-right for booking support.
        </p>
      </main>
      <ChatWidget />
    </>
  );
}
