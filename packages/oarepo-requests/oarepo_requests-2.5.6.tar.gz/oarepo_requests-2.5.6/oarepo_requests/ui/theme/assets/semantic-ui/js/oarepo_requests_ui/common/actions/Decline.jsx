import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import PropTypes from "prop-types";
import { decline, REQUEST_TYPE } from "@js/oarepo_requests_common";
import { RequestActionButton } from "./RequestActionButton";

const Decline = ({ request, extraData, isMutating }) => {
  return (
    <RequestActionButton
      title={i18next.t("Decline request")}
      className="requests request-decline-button"
      negative
      floated="left"
      iconName="cancel"
      isMutating={isMutating}
      action={decline}
      extraData={extraData}
      requestOrRequestType={request}
      buttonLabel={i18next.t("Decline")}
      requireConfirmation={true}
      requestActionName={REQUEST_TYPE.DECLINE}
    />
  );
};

Decline.propTypes = {
  request: PropTypes.object,
  extraData: PropTypes.object,
  isMutating: PropTypes.number,
};

export default Decline;
