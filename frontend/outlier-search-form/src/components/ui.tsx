import * as Collapsible from "@radix-ui/react-collapsible";
import * as Select from "@radix-ui/react-select";
import * as Switch from "@radix-ui/react-switch";
import * as ToggleGroup from "@radix-ui/react-toggle-group";
import { Check, ChevronDown, ChevronUp } from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { ReactNode } from "react";

export function cn(...inputs: Array<string | false | null | undefined>) {
  return twMerge(clsx(inputs));
}

export function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="of-rounded-xl2 of-border of-border-white/8 of-bg-[linear-gradient(180deg,rgba(26,33,64,0.94)_0%,rgba(15,19,36,0.98)_100%)] of-p-6 of-shadow-panel">
      {children}
    </div>
  );
}

export function SectionTitle({ title, copy }: { title: string; copy: string }) {
  return (
    <div className="of-mb-5">
      <div className="of-font-display of-mb-1 of-text-[22px] of-font-bold of-tracking-[-0.03em] of-text-text">
        {title}
      </div>
      <div className="of-max-w-[620px] of-text-sm of-leading-6 of-text-muted">{copy}</div>
    </div>
  );
}

export function FieldLabel({
  label,
  error,
  helper,
}: {
  label: string;
  error?: string;
  helper?: string;
}) {
  return (
    <div className="of-mb-2">
      <div className="of-mb-1 of-text-[13px] of-font-semibold of-leading-5 of-text-text">{label}</div>
      {error ? (
        <div className="of-text-[12px] of-leading-5 of-text-rose-300">{error}</div>
      ) : helper ? (
        <div className="of-text-[12px] of-leading-5 of-text-subtle">{helper}</div>
      ) : null}
    </div>
  );
}

export function TextInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={cn(
        "of-h-[52px] of-w-full of-rounded-[18px] of-border of-border-white/8 of-bg-[#0B1124] of-px-4 of-text-[15px] of-font-medium of-text-text of-outline-none of-transition",
        "placeholder:of-text-subtle focus:of-border-accent-soft focus:of-shadow-[0_0_0_4px_rgba(139,92,246,0.18)]",
        props.className,
      )}
    />
  );
}

export function NumberInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <TextInput {...props} type="number" inputMode="numeric" />;
}

export function Button({
  children,
  variant = "ghost",
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
}) {
  return (
    <button
      {...props}
      className={cn(
        "of-inline-flex of-h-[52px] of-w-full of-items-center of-justify-center of-rounded-[18px] of-border of-px-4 of-text-[15px] of-font-semibold of-transition",
        variant === "primary"
          ? "of-border-accent-soft/20 of-bg-[linear-gradient(90deg,#8B5CF6,#A855F7)] of-text-white of-shadow-glow hover:of-brightness-105"
          : "of-border-white/10 of-bg-white/4 of-text-text hover:of-border-accent-soft/25 hover:of-bg-white/6",
        "disabled:of-cursor-not-allowed disabled:of-opacity-50",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function SelectField({
  value,
  onValueChange,
  options,
}: {
  value: string;
  onValueChange: (value: string) => void;
  options: Array<{ label: string; value: string }>;
}) {
  return (
    <Select.Root value={value} onValueChange={onValueChange}>
      <Select.Trigger className="of-flex of-h-[52px] of-w-full of-items-center of-justify-between of-rounded-[18px] of-border of-border-white/8 of-bg-[#0B1124] of-px-4 of-text-[15px] of-font-medium of-text-text of-outline-none of-transition focus:of-border-accent-soft focus:of-shadow-[0_0_0_4px_rgba(139,92,246,0.18)]">
        <Select.Value />
        <Select.Icon className="of-text-subtle">
          <ChevronDown className="of-h-4 of-w-4" />
        </Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Content
          position="popper"
          sideOffset={8}
          className="of-z-[2000] of-w-[var(--radix-select-trigger-width)] of-overflow-hidden of-rounded-[18px] of-border of-border-white/8 of-bg-[#11162B] of-shadow-panel"
        >
          <Select.Viewport className="of-p-2">
            {options.map((option) => (
              <Select.Item
                key={option.value}
                value={option.value}
                className="of-flex of-cursor-pointer of-items-center of-justify-between of-rounded-xl of-px-3 of-py-2.5 of-text-sm of-text-text of-outline-none hover:of-bg-white/6 data-[highlighted]:of-bg-white/6"
              >
                <Select.ItemText>{option.label}</Select.ItemText>
                <Select.ItemIndicator>
                  <Check className="of-h-4 of-w-4 of-text-accent-soft" />
                </Select.ItemIndicator>
              </Select.Item>
            ))}
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  );
}

export function SegmentedField({
  value,
  onValueChange,
  options,
}: {
  value: string;
  onValueChange: (value: string) => void;
  options: string[];
}) {
  return (
    <ToggleGroup.Root
      type="single"
      value={value}
      onValueChange={(next) => {
        if (next) {
          onValueChange(next);
        }
      }}
      className="of-grid of-h-[52px] of-w-full of-grid-flow-col of-auto-cols-fr of-overflow-hidden of-rounded-[18px] of-border of-border-white/8 of-bg-[#0B1124]"
    >
      {options.map((option) => (
        <ToggleGroup.Item
          key={option}
          value={option}
          className="of-flex of-items-center of-justify-center of-border-r of-border-white/8 of-px-3 of-text-[15px] of-font-semibold of-text-muted of-transition last:of-border-r-0 data-[state=on]:of-bg-accent/18 data-[state=on]:of-text-accent-soft"
        >
          {option}
        </ToggleGroup.Item>
      ))}
    </ToggleGroup.Root>
  );
}

export function VisibilityCard({
  checked,
  onCheckedChange,
}: {
  checked: boolean;
  onCheckedChange: (value: boolean) => void;
}) {
  return (
    <div className="of-flex of-h-full of-flex-col of-justify-between of-rounded-[18px] of-border of-border-white/8 of-bg-white/3 of-p-4">
      <div>
        <div className="of-mb-1 of-text-[13px] of-font-semibold of-text-text">Subscriber Visibility</div>
        <div className="of-text-[12px] of-leading-5 of-text-subtle">
          Keep channels with hidden subscriber counts in the scan when subscriber size is not publicly visible.
        </div>
      </div>
      <label className="of-mt-4 of-flex of-items-center of-justify-between of-gap-3">
        <span className="of-text-sm of-font-medium of-text-text">Include Hidden Subscriber Counts</span>
        <Switch.Root
          checked={checked}
          onCheckedChange={onCheckedChange}
          className="of-relative of-h-7 of-w-12 of-rounded-full of-bg-white/10 of-transition data-[state=checked]:of-bg-accent"
        >
          <Switch.Thumb className="of-block of-h-5 of-w-5 of-translate-x-1 of-rounded-full of-bg-white of-transition will-change-transform data-[state=checked]:of-translate-x-6" />
        </Switch.Root>
      </label>
    </div>
  );
}

export function AdvancedTray({
  open,
  onOpenChange,
  children,
}: {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  children: ReactNode;
}) {
  return (
    <Collapsible.Root open={open} onOpenChange={onOpenChange}>
      <Collapsible.Trigger asChild>
        <button className="of-flex of-h-[52px] of-w-full of-items-center of-justify-between of-rounded-[18px] of-border of-border-white/8 of-bg-white/3 of-px-4 of-text-left of-text-[15px] of-font-semibold of-text-text">
          <span>More Filters</span>
          {open ? <ChevronUp className="of-h-4 of-w-4 of-text-subtle" /> : <ChevronDown className="of-h-4 of-w-4 of-text-subtle" />}
        </button>
      </Collapsible.Trigger>
      <Collapsible.Content className="of-mt-3 of-rounded-[18px] of-border of-border-white/8 of-bg-white/2 of-p-4">
        {children}
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
