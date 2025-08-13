import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import PropTypes from "prop-types";
import { createOrSave, REQUEST_TYPE } from "@js/oarepo_requests_common";
import { RequestActionButton } from "./RequestActionButton";

const Create = ({ requestType, extraData, isMutating }) => {
  return (
    <RequestActionButton
      title={i18next.t("Create request")}
      className="requests request-create-button"
      color="blue"
      floated="right"
      iconName="plus"
      isMutating={isMutating}
      action={createOrSave}
      extraData={extraData}
      requestOrRequestType={requestType}
      buttonLabel={i18next.t("Save")}
      requestActionName={REQUEST_TYPE.CREATE}
      requireConfirmation={extraData?.dangerous}
    />
  );
};

Create.propTypes = {
  requestType: PropTypes.object,
  extraData: PropTypes.object,
  isMutating: PropTypes.number,
};

export default Create;
