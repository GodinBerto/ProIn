export function Logo({ size = 24 }: { size?: number }) {
  return (
    <div
      className="rounded-md bg-primary text-primary-foreground font-bold flex items-center justify-center shrink-0"
      style={{ width: size, height: size, fontSize: size * 0.55 }}
      aria-label="FlowForm"
    >
      F
    </div>
  );
}
