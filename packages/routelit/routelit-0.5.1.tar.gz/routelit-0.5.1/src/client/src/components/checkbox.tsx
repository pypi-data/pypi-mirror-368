import { memo, useCallback } from "react";
import { useFormDispatcherWithAttr } from "../core/context";

const Checkbox = memo(function Checkbox({
  label,
  id,
  required,
  defaultChecked,
  ...props
}: {
  label: string;
  caption?: string;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange">) {
  const dispatchChange = useFormDispatcherWithAttr(id!, "change", "checked");
  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      dispatchChange(e.target.checked);
    },
    [dispatchChange]
  );
  return (
    <div className="rl-form-flex-control">
      <input
        {...props}
        type="checkbox"
        id={id}
        defaultChecked={defaultChecked}
        onChange={onChange}
        required={required}
      />
      <label htmlFor={id}>
        {label} {required && <span className="rl-required">*</span>}
      </label>
    </div>
  );
});

Checkbox.displayName = "Checkbox";

export default Checkbox;
