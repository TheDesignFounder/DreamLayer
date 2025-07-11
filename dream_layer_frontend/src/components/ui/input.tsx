import * as React from "react"

import { cn } from "@/lib/utils"

interface InputProps extends React.ComponentProps<"input"> {
  required?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, required, value, ...props }, ref) => {
    // Check if field is required and empty
    const isRequiredAndEmpty = required && (!value || (typeof value === 'string' && value.trim() === ''));

    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
          isRequiredAndEmpty ? 'ring-2 ring-red-500' : '',
          className
        )}
        ref={ref}
        value={value}
        required={required}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
