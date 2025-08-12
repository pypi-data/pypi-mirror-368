import { memo, useCallback } from "react";
import { useFormDispatcherWithAttr } from "../core/context";

type CheckboxGroupProps = {
  id: string;
  label: string;
  value: string[];
  required?: boolean;
  flexDirection?: "row" | "col";
  options: Array<{ label: string; value: string; caption?: string; disabled?: boolean }>;
};

function CheckboxGroupOption(props: {
  option: CheckboxGroupProps["options"][number];
  id: string;
  value: string[];
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  const { id, value, onChange } = props;

  const option: CheckboxGroupProps["options"][number] =
    props.option;

  return (
    <div key={option.value} className="rl-form-flex-control">
      <input
        disabled={option.disabled}
        type="checkbox"
        value={option.value}
        id={`${id}-${option.value}`}
        checked={value.includes(option.value)}
        onChange={onChange}
      />
      <div className="rl-form-inline-label">
        <label htmlFor={`${id}-${option.value}`}>{option.label}</label>
        {option.caption && (
          <small className="rl-form-control-caption">{option.caption}</small>
        )}
      </div>
    </div>
  );
}

const CheckboxGroup = memo(function CheckboxGroup({
  id,
  label,
  value,
  required,
  options,
  flexDirection = "col",
}: CheckboxGroupProps) {
  const dispatchChange = useFormDispatcherWithAttr(id, "change", "value");
  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.checked
        ? [...value, e.target.value]
        : value.filter((v) => v !== e.target.value);
      dispatchChange(newValue);
    },
    [dispatchChange, value]
  );
  return (
    <div className="rl-form-group">
      {label && (
        <label>
          {label} {required && <span className="rl-required">*</span>}
        </label>
      )}
      <div className={`rl-form-control-group rl-flex-${flexDirection}`}>
        {options.map((option) => (
          <CheckboxGroupOption
            key={typeof option === "string" ? option : option.value}
            id={id}
            value={value}
            onChange={onChange}
            option={option}
          />
        ))}
      </div>
    </div>
  );
});

CheckboxGroup.displayName = "CheckboxGroup";

export default CheckboxGroup;
