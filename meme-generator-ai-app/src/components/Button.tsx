type ButtonProps = {
  children?: React.ReactNode;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  className?: string;
};

const Button: React.FC<ButtonProps> = (props) => {
  return (
    <button
      className={
        " mt-5 px-6 py-3 rounded-full  text-white text-lg font-medium hover:bg-blue-400 transition hover:scale-102 duration-100 ease-in-out " +
        props.className
      }
      onClick={props.onClick}
    >
      {props.children}
    </button>
  );
};

export default Button;
