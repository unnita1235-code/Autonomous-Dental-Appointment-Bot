export default function LiveConversationsPage(): JSX.Element {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6">
      <h1 className="font-heading text-2xl font-semibold text-slate-900">Live Conversations</h1>
      <p className="mt-2 text-sm text-muted">
        Use the Overview handoff queue and real-time socket events to prioritize active patient conversations.
      </p>
    </section>
  );
}
