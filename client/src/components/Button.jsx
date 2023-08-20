import { cls } from "libs/utils";

const Button = ({ text, main = false, ...rest }) => {
  const customCls = rest.className ? rest.className : "";
  return (
    <button
      {...rest}
      className={cls(
        "flex flex-col w-full items-center justify-center m-1 py-2 px-4 border",
        main
          ? "border-transparent rounded-md shadow-sm bg-teal-400 hover:bg-teal-600 text-white text-sm font-medium focus:ring-2 focus:ring-offset-2 focus:ring-teal-400 focus:outline-none"
          : "m-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white hover:bg-gray-50 text-gray-500 text-sm font-medium",
        customCls
      )}
    >
      {text}
    </button>
  );
};

export default Button;
