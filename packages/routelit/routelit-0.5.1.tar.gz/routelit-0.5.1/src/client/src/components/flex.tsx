import { ComponentProps, useMemo } from "react";

interface FlexProps extends ComponentProps<"div"> {
  children: React.ReactNode;
  direction?: "row" | "col";
  flexWrap?: "wrap" | "nowrap";
  justifyContent?: "start" | "end" | "center" | "between" | "around" | "evenly";
  alignItems?: "normal" | "start" | "end" | "center" | "baseline" | "stretch";
  alignContent?:
    | "normal"
    | "start"
    | "end"
    | "center"
    | "between"
    | "around"
    | "evenly";
  gap?: string;
}

function Flex({
  children,
  direction = "col",
  flexWrap = "nowrap",
  justifyContent = "start",
  alignItems = "normal",
  alignContent = "normal",
  gap = "0",
  ...props
}: FlexProps) {
  const style = useMemo(
    () => ({
      ...props.style,
      gap: gap,
      justifyContent: justifyContent,
      alignItems: alignItems,
      alignContent: alignContent,
    }),
    [gap, justifyContent, alignItems, alignContent, props.style]
  );
  const className = useMemo(() => {
    return `rl-flex rl-flex-${direction} ${
      flexWrap === "wrap" ? "rl-flex-wrap" : ""
    }`;
  }, [direction, flexWrap]);
  return (
    <div className={className} style={style} {...props}>
      {children}
    </div>
  );
}

export default Flex;
