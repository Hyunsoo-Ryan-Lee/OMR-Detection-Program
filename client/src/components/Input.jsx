import { cls } from "libs/utils";

const Input = ({ text, large = false, ...rest }) => {
  return (
    <input
      {...rest}
      className={cls(
        "apperance-none border w-full border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-teal-400 focus:border-teal-400",
        large ? "px-3 py-3" : "px-1 py-1"
      )}
    />
  );
};

export default Input;
