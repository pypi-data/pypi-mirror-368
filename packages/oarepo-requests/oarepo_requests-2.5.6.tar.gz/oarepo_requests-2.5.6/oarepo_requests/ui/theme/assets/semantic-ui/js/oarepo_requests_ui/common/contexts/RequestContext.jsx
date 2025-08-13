import React, { createContext, useContext } from "react";
import PropTypes from "prop-types";

const RequestContext = createContext();

export const RequestContextProvider = ({ children, value }) => {
  return (
    <RequestContext.Provider value={value}>{children}</RequestContext.Provider>
  );
};

RequestContextProvider.propTypes = {
  value: PropTypes.object,
  children: PropTypes.node,
};

export const useRequestContext = () => {
  const context = useContext(RequestContext);
  if (!context) {
    console.warn(
      "useRequestContext must be used inside RequestContext.Provider"
    );
  }
  return context;
};
