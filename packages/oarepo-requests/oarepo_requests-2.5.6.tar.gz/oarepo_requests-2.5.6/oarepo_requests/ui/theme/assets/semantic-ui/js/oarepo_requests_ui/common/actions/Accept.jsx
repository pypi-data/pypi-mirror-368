import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import PropTypes from "prop-types";
import { accept, REQUEST_TYPE } from "@js/oarepo_requests_common";
import { RequestActionButton } from "./RequestActionButton";

const Accept = ({ request, extraData, isMutating }) => {
  return (
    <RequestActionButton
      title={i18next.t("Accept request")}
      className="requests request-accept-button"
      positive={!extraData?.dangerous}
      negative={extraData?.dangerous}
      floated="right"
      iconName="check"
      isMutating={isMutating}
      action={accept}
      extraData={extraData}
      requestOrRequestType={request}
      buttonLabel={request.name || i18next.t("Accept")}
      requestActionName={REQUEST_TYPE.ACCEPT}
      requireConfirmation={extraData?.dangerous}
    />
  );
};

Accept.propTypes = {
  request: PropTypes.object,
  extraData: PropTypes.object,
  isMutating: PropTypes.number,
};

export default Accept;
