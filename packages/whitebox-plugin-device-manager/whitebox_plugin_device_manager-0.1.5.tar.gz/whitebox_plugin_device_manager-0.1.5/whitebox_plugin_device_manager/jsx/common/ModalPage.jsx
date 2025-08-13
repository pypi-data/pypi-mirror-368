const ModalPage = ({ topNav = null, innerClassName = null, ...props }) => {
  return (
    <div
      className="c_modal_page
                      h-dvh flex
                      items-center justify-center
                      bg-white
                      md:bg-low-emphasis"
    >
      <div
        className={
          `flex flex-col
                         h-dvh
                         bg-white rounded-lg max-w-xl w-full
                         md:h-auto
                         md:max-h-[calc(100%-4rem)]
                         md:rounded-xl
                         md:shadow-md` +
          (innerClassName ? " " + innerClassName : "")
        }
      >
        {topNav}

        {props.children}
      </div>
    </div>
  );
};

export default ModalPage;
