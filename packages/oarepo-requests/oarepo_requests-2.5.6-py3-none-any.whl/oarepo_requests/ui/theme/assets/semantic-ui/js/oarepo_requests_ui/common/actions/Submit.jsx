import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import PropTypes from "prop-types";
import { saveAndSubmit, REQUEST_TYPE } from "@js/oarepo_requests_common";
import { RequestActionButton } from "./RequestActionButton";

const Submit = ({ request, extraData, isMutating }) => {
  return (
    <RequestActionButton
      title={i18next.t("Submit request")}
      className="requests request-submit-button"
      color="blue"
      floated="right"
      iconName="paper plane"
      isMutating={isMutating}
      action={saveAndSubmit}
      extraData={extraData}
      requestOrRequestType={request}
      buttonLabel={i18next.t("Submit")}
      requestActionName={REQUEST_TYPE.SUBMIT}
      requireConfirmation={extraData?.dangerous}
    />
  );
};

Submit.propTypes = {
  request: PropTypes.object,
  extraData: PropTypes.object,
  isMutating: PropTypes.number,
};

export default Submit;
