import React from "react";
import { Message, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_requests_ui/i18next";

export const WarningMessage = ({ message, ...uiProps }) => {
  return (
    <Message negative {...uiProps} className="rel-mr-1 rel-ml-1 rel-mb-1">
      <Message.Header>
        <Icon name="warning sign" className="rel-mr-1" />
        {message}
      </Message.Header>
    </Message>
  );
};

WarningMessage.propTypes = {
  message: PropTypes.string,
};

WarningMessage.defaultProps = {
  message: i18next.t(
    "Are you sure you want to proceed? Once the action is completed, it will not be possible to undo it."
  ),
};
