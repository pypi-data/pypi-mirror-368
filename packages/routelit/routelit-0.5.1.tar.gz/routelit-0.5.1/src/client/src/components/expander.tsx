const Expander = ({
  title,
  open,
  children,
}: {
  title: string;
  open: boolean;
  children: React.ReactNode;
}) => {
  return (
    <details open={open}>
      <summary>{title}</summary>
      {children}
    </details>
  );
};

Expander.displayName = "Expander";

export default Expander;
