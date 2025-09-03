type CaptionProps = {
  text?: string;
};

const Caption: React.FC<CaptionProps> = (props) => {
  return (
    <>
      <p className="font-semibold text-lg md:text-xl lg:text-2xl p-3 text-slate-800 max-w-170 text-center">
        {props.text}
      </p>
    </>
  );
};

export default Caption;
