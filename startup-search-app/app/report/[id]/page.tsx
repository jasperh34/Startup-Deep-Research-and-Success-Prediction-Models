import { AppShell } from "@/components/AppShell";
import { ReportView } from "@/components/report/ReportView";

export default async function ReportPage({
  params,
}: Readonly<{
  params: Promise<{ id: string }>;
}>) {
  const { id } = await params;

  return (
    <AppShell>
      <ReportView id={id} />
    </AppShell>
  );
}
