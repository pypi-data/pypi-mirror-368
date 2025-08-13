import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";


export const ConfirmationModalCancelButton = (uiProps) => (
    <Button
      content={i18next.t("Cancel")}
      className="requests confirmation-modal-cancel-button"
      {...uiProps}
    />
  );