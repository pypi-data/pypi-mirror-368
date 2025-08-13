import React from "react";
import { Label, Icon } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_dashboard";
import PropTypes from "prop-types";

export const LabelStatusCreate = (props) => {
  return (
    <Label horizontal className="primary" size="small">
      <Icon name="times rectangle" />
      {i18next.t("Not submitted")}
    </Label>
  );
};

export const RequestTypeLabel = ({ requestName }) => {
  return (
    <Label horizontal size="small">
      {requestName}
    </Label>
  );
};

RequestTypeLabel.propTypes = {
  requestName: PropTypes.string.isRequired,
};
