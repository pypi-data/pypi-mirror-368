import React from "react";
import PropTypes from "prop-types";
import { useFormikContext, getIn } from "formik";

export const DefaultView = ({ fieldPath, label }) => {
  const { values } = useFormikContext();
  const value = getIn(values, fieldPath, "");
  return value ? (
    <div>
      <strong>{label}</strong>: <span>{value}</span>
    </div>
  ) : null;
};

DefaultView.propTypes = {
  fieldPath: PropTypes.string,
  label: PropTypes.string,
};

export default DefaultView;
