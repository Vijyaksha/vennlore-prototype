import { BottomNav } from "@/components/bottom-nav";

export default async function TalkLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <>
      {children}
      <BottomNav talkId={Number(id)} />
    </>
  );
}
