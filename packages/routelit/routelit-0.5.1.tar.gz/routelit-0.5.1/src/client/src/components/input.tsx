import { memo } from "react";
import { useInputChangeEvent } from "../core/hooks";

function TextInputComponent({
  id,
  label,
  defaultValue,
  type = "text",
  ...props
}: {
  id: string;
  label?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  const { handleBlur, handleKeyDown } = useInputChangeEvent(id, defaultValue as string);
  const required = props.required;
  return (
    <div className="rl-form-group">
      {label && <label htmlFor={id}>{label} {required && <span className="rl-required">*</span>}</label>}
      <input
        type={type}
        id={id}
        {...props}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        defaultValue={defaultValue}
      />
    </div>
  );
}

const TextInput = memo(TextInputComponent);
TextInput.displayName = "TextInput";

export default TextInput;
