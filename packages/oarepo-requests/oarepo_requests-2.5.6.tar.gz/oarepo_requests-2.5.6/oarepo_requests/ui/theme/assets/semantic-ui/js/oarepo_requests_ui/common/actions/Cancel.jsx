import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import PropTypes from "prop-types";
import { cancel, REQUEST_TYPE } from "@js/oarepo_requests_common";
import { RequestActionButton } from "./RequestActionButton";

const Cancel = ({ request, isMutating, extraData }) => {
  return (
    <RequestActionButton
      title={i18next.t("Cancel request")}
      className="requests request-cancel-button"
      floated="left"
      iconName="trash alternate"
      color="grey"
      isMutating={isMutating}
      action={cancel}
      extraData={extraData}
      requestOrRequestType={request}
      buttonLabel={i18next.t("Cancel")}
      requestActionName={REQUEST_TYPE.CANCEL}
      requireConfirmation={false}
    />
  );
};

Cancel.propTypes = {
  request: PropTypes.object,
  isMutating: PropTypes.number,
  extraData: PropTypes.object,
};

export default Cancel;
