import { cn } from "../../lib/utils";

export function Input({ className, label, error, ...props }) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-gray-700">{label}</label>
      )}
      <input
        className={cn(
          "px-3 py-2 border rounded-lg text-sm outline-none transition",
          "border-gray-300 focus:border-primary-500 focus:ring-1 focus:ring-primary-500",
          error && "border-red-500 focus:border-red-500 focus:ring-red-500",
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
