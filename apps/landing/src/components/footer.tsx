import { Logo } from "@repo/ui";

export default function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-8 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Logo size={20} />
          <span>FlowForm</span>
        </div>
        <div>© {new Date().getFullYear()} FlowForm</div>
      </div>
    </footer>
  );
}
