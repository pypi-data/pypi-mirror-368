import React, { createContext, useContext } from "react";
import PropTypes from "prop-types";

const CallbackContext = createContext();

export const CallbackContextProvider = ({ children, value }) => {
  return (
    <CallbackContext.Provider value={value}>
      {children}
    </CallbackContext.Provider>
  );
};

CallbackContextProvider.propTypes = {
  value: PropTypes.object.isRequired,
  children: PropTypes.node,
};

export const useCallbackContext = () => {
  const context = useContext(CallbackContext);
  if (!context) {
    console.warn(
      "useCallbackContext must be used inside CallbackContext.Provider"
    );
  }
  return context;
};
