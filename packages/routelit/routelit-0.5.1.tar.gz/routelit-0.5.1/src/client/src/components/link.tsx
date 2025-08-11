import { useLinkClickHandler } from "../core/hooks";

interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  isExternal?: boolean;
  text?: string;
  replace?: boolean;
}

function Link(props: LinkProps) {
  const { id, href, text, children, replace, isExternal, ...rest } = props;
  const handleClick = useLinkClickHandler({
    id: id!,
    href: href!,
    replace,
    isExternal,
  });
  return (
    <a id={id} href={href} onClick={handleClick} {...rest}>
      {text || children}
    </a>
  );
}

export default Link;
