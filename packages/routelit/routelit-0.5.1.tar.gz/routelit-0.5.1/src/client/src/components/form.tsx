import { createContext, useContext } from "react";

interface FormProps {
  id: string;
  children: React.ReactNode;
}

const FormContext = createContext<Pick<FormProps, "id">>({ id: "" });

export function useFormId(): string | undefined {
  const context = useContext(FormContext);
  return context.id;
}

function Form({ id, children }: FormProps) {
  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
  }
  return (
    <FormContext.Provider value={{ id }}>
      <form id={id} data-testid={id} onSubmit={handleSubmit}>{children}</form>
    </FormContext.Provider>
  );
}

export default Form;
