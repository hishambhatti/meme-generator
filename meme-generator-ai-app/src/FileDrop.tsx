import React from "react";

type FileDropProps = {
  children?: React.ReactNode;
  onChangeEvent?: React.ChangeEventHandler<HTMLInputElement>;
};

const FileDrop: React.FC<FileDropProps> = (props) => {
  const content = props.children;
  const onChangeEventHandler = props.onChangeEvent;

  return (
    <>
      <label
        htmlFor="file-input"
        className="flex grow justify-center items-center m-10 max-w-2xl w-full h-48 md:h-64 lg:h-72 rounded-4xl bg-blue-50 border-4 border-dotted border-slate-400 hover:border-5"
      >
        <p className="px-5 text-md md:text-lg lg:text-xl italic text-slate-400 text-center">
          {content}
        </p>
      </label>

      <input
        type="file"
        accept=".png,.jpg,.jpeg"
        className="hidden"
        onChange={onChangeEventHandler}
        id="file-input"
      />
    </>
  );
};

export default FileDrop;
