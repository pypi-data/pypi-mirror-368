const ModalTopNav = ({
  text,
  leadingButtons = null,
  trailingButtons = null,
}) => {
  return (
    <div
      className="flex h-14 text-full-emphasis font-bold
                       items-start justify-center gap-5 pt-2
                      md:px-2"
    >
      <div className="flex flex-1 w-max">
        <div className="flex">{leadingButtons}</div>
      </div>

      <div className="flex h-12 justify-center items-center gap-2">
        <p className="text-lg md:text-xl">{text}</p>
      </div>

      <div className="flex flex-1">
        <div className="flex ml-auto">{trailingButtons}</div>
      </div>
    </div>
  );
};

export default ModalTopNav;
