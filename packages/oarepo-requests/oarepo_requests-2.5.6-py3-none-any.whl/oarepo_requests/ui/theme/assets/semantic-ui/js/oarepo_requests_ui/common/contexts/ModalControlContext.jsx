import React, { createContext, useContext } from "react";
import PropTypes from "prop-types";

const ModalControlContext = createContext();

export const ModalControlContextProvider = ({ children, value }) => {
  return (
    <ModalControlContext.Provider value={value}>
      {children}
    </ModalControlContext.Provider>
  );
};

ModalControlContextProvider.propTypes = {
  value: PropTypes.object.isRequired,
  children: PropTypes.node,
};

export const useModalControlContext = () => {
  const context = useContext(ModalControlContext);
  if (!context) {
    console.warn(
      "useModalControlContext must be used inside ModalControlContext.Provider"
    );
  }
  return context;
};
