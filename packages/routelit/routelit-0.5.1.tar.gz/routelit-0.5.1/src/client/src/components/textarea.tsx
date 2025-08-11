import { memo } from "react";
import { useInputChangeEvent } from "../core/hooks";

function TextareaComponent({
  id,
  label,
  defaultValue,
  ...props
}: {
  id: string;
  label?: string;
} & React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const { handleBlur, handleKeyDown } = useInputChangeEvent(id, defaultValue as string);
  const required = props.required;
  return (
    <div className="rl-form-group">
      {label && <label htmlFor={id}>{label} {required && <span className="rl-required">*</span>}</label>}
      <textarea
        id={id}
        {...props}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        defaultValue={defaultValue}
      />
    </div>
  );
}

const Textarea = memo(TextareaComponent);
Textarea.displayName = "Textarea";

export default Textarea;
